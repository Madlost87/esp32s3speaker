#include "galileo_audio_tap.h"

#include <algorithm>
#include <inttypes.h>
#include <cstring>

#include <fcntl.h>
#include <lwip/inet.h>
#include <lwip/sockets.h>

#include "esphome/core/log.h"

namespace esphome::galileo_audio_tap {

static const char *const TAG = "galileo_audio_tap";

namespace {

int hex_value(char value) {
  if (value >= '0' && value <= '9')
    return value - '0';
  if (value >= 'a' && value <= 'f')
    return value - 'a' + 10;
  if (value >= 'A' && value <= 'F')
    return value - 'A' + 10;
  return -1;
}

}  // namespace

void GalileoAudioTap::set_session_id(const std::string &session_id) {
  for (size_t index = 0; index < this->session_id_.size(); index++) {
    const int high = hex_value(session_id[index * 2]);
    const int low = hex_value(session_id[index * 2 + 1]);
    this->session_id_[index] = static_cast<uint8_t>((high << 4) | low);
  }
}

void GalileoAudioTap::setup() {
  if (this->microphone_ == nullptr) {
    ESP_LOGE(TAG, "microphone is required");
    this->mark_failed();
    return;
  }
  this->microphone_->add_data_callback([this](const std::vector<uint8_t> &data) { this->on_microphone_data_(data); });
  this->register_service(&GalileoAudioTap::start_capture, "galileo_audio_tap_start", {"session_id"});
  this->register_service(&GalileoAudioTap::stop_capture, "galileo_audio_tap_stop", {"session_id"});
}

void GalileoAudioTap::dump_config() {
  ESP_LOGCONFIG(TAG, "Galileo Audio Tap:");
  ESP_LOGCONFIG(TAG, "  Destination: %s:%u", this->host_.c_str(), this->port_);
  ESP_LOGCONFIG(TAG, "  Armed: %s", YESNO(this->armed_));
  ESP_LOGCONFIG(TAG, "  Mode: bounded PCM capture only; idle until authenticated API start");
}

bool GalileoAudioTap::session_matches_(const std::string &provided) const {
  if (provided.size() != 16)
    return false;
  uint8_t difference = 0;
  for (size_t index = 0; index < this->session_id_.size(); index++) {
    const int high = hex_value(provided[index * 2]);
    const int low = hex_value(provided[index * 2 + 1]);
    if (high < 0 || low < 0)
      return false;
    difference |= this->session_id_[index] ^ static_cast<uint8_t>((high << 4) | low);
  }
  return difference == 0;
}

void GalileoAudioTap::start_capture(std::string session_id) {
  if (!this->armed_ || !this->session_matches_(session_id)) {
    ESP_LOGW(TAG, "Rejected audio-tap start request");
    return;
  }
  if (this->capture_active_)
    return;
  if (!this->open_socket_() || !this->send_control_(PACKET_OPEN)) {
    ESP_LOGW(TAG, "Unable to open audio-tap capture session");
    return;
  }
  this->sequence_ = 0;
  this->sample_offset_ = 0;
  this->capture_active_ = true;
  ESP_LOGI(TAG, "Audio-tap capture session opened");
}

void GalileoAudioTap::start_capture_from_wake_word() {
  if (!this->armed_ || this->capture_active_)
    return;
  if (!this->open_socket_() || !this->send_control_(PACKET_OPEN)) {
    ESP_LOGW(TAG, "Unable to open wake-word audio-tap session");
    return;
  }
  this->sequence_ = 0;
  this->sample_offset_ = 0;
  this->capture_active_ = true;
  ESP_LOGI(TAG, "Audio-tap capture opened from wake word");
}

void GalileoAudioTap::stop_capture_from_timeout() {
  if (!this->capture_active_)
    return;
  this->send_control_(PACKET_CLOSE);
  this->capture_active_ = false;
  this->pending_size_ = 0;
  ESP_LOGI(TAG, "Audio-tap capture closed by timeout");
}

void GalileoAudioTap::stop_capture(std::string session_id) {
  if (!this->capture_active_ || !this->session_matches_(session_id))
    return;
  this->send_control_(PACKET_CLOSE);
  this->capture_active_ = false;
  this->pending_size_ = 0;
  ESP_LOGI(TAG, "Audio-tap capture session closed, dropped frames=%" PRIu32, this->dropped_frames_);
}

bool GalileoAudioTap::send_control_(uint8_t packet_type) {
  if (!this->open_socket_())
    return false;
  std::array<uint8_t, HEADER_BYTES> packet{};
  std::memcpy(packet.data(), "GLA1", 4);
  packet[4] = 1;
  packet[5] = packet_type;
  std::memcpy(packet.data() + 6, this->session_id_.data(), this->session_id_.size());

  sockaddr_in destination{};
  destination.sin_family = AF_INET;
  destination.sin_port = htons(this->port_);
  if (inet_aton(this->host_.c_str(), &destination.sin_addr) == 0)
    return false;
  return lwip_sendto(this->socket_, packet.data(), packet.size(), 0, reinterpret_cast<sockaddr *>(&destination),
                     sizeof(destination)) == static_cast<int>(packet.size());
}

bool GalileoAudioTap::open_socket_() {
  if (this->socket_ >= 0)
    return true;
  this->socket_ = lwip_socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if (this->socket_ < 0) {
    ESP_LOGW(TAG, "Unable to open UDP socket");
    return false;
  }
  const int flags = fcntl(this->socket_, F_GETFL, 0);
  if (flags >= 0)
    fcntl(this->socket_, F_SETFL, flags | O_NONBLOCK);
  return true;
}

void GalileoAudioTap::on_microphone_data_(const std::vector<uint8_t> &data) {
  if (!this->capture_active_ || data.empty())
    return;

  const size_t frame_size = std::min(data.size(), MAX_PCM_BYTES);
  portENTER_CRITICAL(&this->mutex_);
  if (this->pending_size_ != 0) {
    this->dropped_frames_++;
  } else {
    std::memcpy(this->pending_pcm_.data(), data.data(), frame_size);
    this->pending_size_ = frame_size;
  }
  portEXIT_CRITICAL(&this->mutex_);
}

void GalileoAudioTap::loop() {
  if (!this->capture_active_ || this->pending_size_ == 0 || !this->open_socket_())
    return;

  std::array<uint8_t, HEADER_BYTES + MAX_PCM_BYTES> packet{};
  size_t frame_size = 0;
  portENTER_CRITICAL(&this->mutex_);
  frame_size = this->pending_size_;
  if (frame_size != 0) {
    std::memcpy(packet.data() + HEADER_BYTES, this->pending_pcm_.data(), frame_size);
    this->pending_size_ = 0;
  }
  portEXIT_CRITICAL(&this->mutex_);
  if (frame_size == 0)
    return;

  std::memcpy(packet.data(), "GLA1", 4);
  packet[4] = 1;
  packet[5] = PACKET_PCM;
  std::memcpy(packet.data() + 6, this->session_id_.data(), this->session_id_.size());
  const uint32_t sequence = htonl(this->sequence_++);
  const uint32_t sample_offset = htonl(this->sample_offset_);
  const uint16_t payload_size = htons(static_cast<uint16_t>(frame_size));
  std::memcpy(packet.data() + 14, &sequence, sizeof(sequence));
  std::memcpy(packet.data() + 18, &sample_offset, sizeof(sample_offset));
  std::memcpy(packet.data() + 22, &payload_size, sizeof(payload_size));
  this->sample_offset_ += static_cast<uint32_t>(frame_size / 2);

  sockaddr_in destination{};
  destination.sin_family = AF_INET;
  destination.sin_port = htons(this->port_);
  if (inet_aton(this->host_.c_str(), &destination.sin_addr) == 0) {
    ESP_LOGW(TAG, "Invalid IPv4 destination");
    return;
  }
  const int sent = lwip_sendto(this->socket_, packet.data(), HEADER_BYTES + frame_size, 0,
                               reinterpret_cast<sockaddr *>(&destination), sizeof(destination));
  if (sent < 0) {
    this->dropped_frames_++;
  }
}

}  // namespace esphome::galileo_audio_tap

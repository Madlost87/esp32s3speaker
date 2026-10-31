#include "galileo_audio_tap.h"

#include <algorithm>
#include <cstdlib>
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

bool valid_response_id(const std::string &value) {
  if (value.size() != 32)
    return false;
  return std::all_of(value.begin(), value.end(), [](char character) {
    return character >= '0' && character <= '9' || character >= 'a' && character <= 'f';
  });
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
  // lwIP is not guaranteed to be ready while ESPHome invokes component
  // setup().  Opening the socket here can assert in FreeRTOS after an OTA
  // boot, which then triggers ESPHome's automatic rollback.  loop() opens
  // it once the network stack is running and retries safely if Wi-Fi is not
  // ready yet.
  this->register_service(&GalileoAudioTap::start_capture, "galileo_audio_tap_start", {"session_id"});
  this->register_service(&GalileoAudioTap::stop_capture, "galileo_audio_tap_stop", {"session_id"});
  if (this->media_player_ != nullptr)
    this->register_service(&GalileoAudioTap::play_direct_tts, "galileo_direct_tts", {"url"});
  if (this->media_player_ != nullptr) {
    this->media_player_->add_on_state_callback([this](media_player::MediaPlayerState state) {
      if (this->direct_tts_pending_ && state == media_player::MEDIA_PLAYER_STATE_ANNOUNCING)
        this->direct_tts_announcing_ = true;
      // speaker_source can publish a delayed IDLE from the previous
      // announcement after a new URL was accepted. Ignore non-announcing
      // transitions during the short start guard; only the new announcement
      // may be allowed to finish itself.
      if (this->direct_tts_announcing_ && state != media_player::MEDIA_PLAYER_STATE_ANNOUNCING &&
          millis() - this->direct_tts_started_at_ >= 500)
        this->finish_direct_tts_();
    });
  }
}

void GalileoAudioTap::play_direct_tts(std::string url) {
  if (!this->armed_ || this->media_player_ == nullptr || url.empty()) {
    ESP_LOGW(TAG, "Rejected direct TTS request");
    return;
  }
  // A VAD dialogue capture can end while the previous announcement pipeline
  // is still releasing its final buffers. Force a clean player boundary and
  // schedule the new URL one loop later; otherwise speaker_source can accept
  // the HTTP transfer but leave it inaudible in the old announcement state.
  this->cancel_timeout("direct-tts-start");
  ESP_LOGI(TAG, "Direct TTS received; player state=%d pending=%s announcing=%s",
           static_cast<int>(this->media_player_->state), YESNO(this->direct_tts_pending_),
           YESNO(this->direct_tts_announcing_));
  if (this->media_player_->state == media_player::MEDIA_PLAYER_STATE_IDLE) {
    // Do not send STOP to an already-idle player: speaker_source publishes a
    // delayed idle callback for that no-op, which can otherwise close the
    // announcement just started by the dialogue follow-up.
    this->start_direct_tts_(url);
    return;
  }
  this->media_player_->make_call().set_command(media_player::MEDIA_PLAYER_COMMAND_STOP).perform();
  this->set_timeout("direct-tts-start", 50, [this, url]() { this->start_direct_tts_when_idle_(url, "", 0); });
}

void GalileoAudioTap::start_direct_tts_when_idle_(std::string url, std::string response_id, uint8_t retries) {
  if (this->media_player_ == nullptr)
    return;
  if (this->media_player_->state != media_player::MEDIA_PLAYER_STATE_IDLE && retries < 20) {
    this->set_timeout("direct-tts-start", 50, [this, url, response_id, retries]() {
      this->start_direct_tts_when_idle_(url, response_id, retries + 1);
    });
    return;
  }
  if (this->media_player_->state != media_player::MEDIA_PLAYER_STATE_IDLE)
    ESP_LOGW(TAG, "Player did not reach idle before direct TTS; forcing start");
  this->start_direct_tts_(url, response_id);
}

void GalileoAudioTap::start_direct_tts_(std::string url, std::string response_id) {
  if (!this->armed_ || this->media_player_ == nullptr)
    return;
  this->direct_tts_pending_ = true;
  this->direct_tts_announcing_ = false;
  this->direct_tts_response_id_ = response_id;
  this->direct_tts_started_at_ = millis();
  this->trigger_all_(this->tts_started_triggers_);
  if (!response_id.empty())
    this->send_lifecycle_("tts_started");
  this->media_player_->make_call().set_media_url(url).set_announcement(true).perform();
  this->set_timeout("direct-tts-announcement-timeout", 30000, [this]() { this->finish_direct_tts_(); });
  ESP_LOGI(TAG, "Started direct TTS announcement after clean player boundary; player state=%d",
           static_cast<int>(this->media_player_->state));
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
  this->reset_endpoint_detector_();
  this->capture_active_ = true;
  this->trigger_all_(this->capture_started_triggers_);
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
  this->reset_endpoint_detector_();
  this->capture_active_ = true;
  this->trigger_all_(this->capture_started_triggers_);
  ESP_LOGI(TAG, "Audio-tap capture opened from wake word");
}

void GalileoAudioTap::start_capture_from_dialogue_vad() {
  if (!this->dialogue_active_ || this->capture_active_)
    return;
  this->dialogue_active_ = false;
  this->capture_response_id_ = this->dialogue_response_id_;
  ESP_LOGI(TAG, "Dialogue VAD accepted; opening follow-up capture");
  this->cancel_timeout("direct-dialogue-window");
  this->start_capture_from_wake_word();
}

void GalileoAudioTap::stop_capture_from_timeout() {
  this->close_capture_("external timeout");
}

void GalileoAudioTap::stop_capture(std::string session_id) {
  if (!this->capture_active_ || !this->session_matches_(session_id))
    return;
  this->close_capture_("API request");
}

void GalileoAudioTap::reset_endpoint_detector_() {
  this->captured_samples_ = 0;
  this->silence_samples_ = 0;
  this->speech_detected_ = false;
  this->endpoint_detected_ = false;
  this->noise_floor_ = 0;
}

void GalileoAudioTap::close_capture_(const char *reason) {
  if (!this->capture_active_)
    return;
  this->send_control_(PACKET_CLOSE);
  if (!this->capture_response_id_.empty()) {
    this->send_lifecycle_("capture_released");
    this->capture_response_id_.clear();
  }
  this->capture_active_ = false;
  this->pending_size_ = 0;
  this->trigger_all_(this->capture_finished_triggers_);
  ESP_LOGI(TAG, "Audio-tap capture closed (%s), dropped frames=%" PRIu32, reason, this->dropped_frames_);
}

void GalileoAudioTap::finish_direct_tts_() {
  if (!this->direct_tts_pending_)
    return;
  this->cancel_timeout("direct-tts-announcement-timeout");
  this->direct_tts_pending_ = false;
  this->direct_tts_announcing_ = false;
  this->last_completed_response_id_ = this->direct_tts_response_id_;
  if (!this->direct_tts_response_id_.empty())
    this->send_lifecycle_("tts_finished");
  ESP_LOGI(TAG, "Direct TTS finished; player state=%d dialogue_pending=%s",
           this->media_player_ == nullptr ? -1 : static_cast<int>(this->media_player_->state),
           YESNO(this->dialogue_pending_));
  this->trigger_all_(this->tts_finished_triggers_);
  if (this->dialogue_pending_) {
    this->dialogue_pending_ = false;
    this->dialogue_active_ = true;
    this->set_timeout("direct-dialogue-window", this->dialogue_seconds_ * 1000U, [this]() {
      this->dialogue_active_ = false;
      ESP_LOGI(TAG, "Direct dialogue window expired");
    });
    ESP_LOGI(TAG, "Direct dialogue window armed for %u seconds", this->dialogue_seconds_);
  }
}

void GalileoAudioTap::arm_dialogue_(uint16_t seconds, const std::string &response_id) {
  if (!this->dialogue_enabled_ || seconds == 0 || seconds > 30 || !valid_response_id(response_id) ||
      response_id != this->last_completed_response_id_)
    return;
  this->dialogue_seconds_ = seconds;
  // Core sends this immediately before the matching TTS command. Do not make
  // the microphone eligible until that announcement has fully released its
  // audio pipeline.
  this->dialogue_active_ = false;
  this->dialogue_pending_ = true;
  this->dialogue_response_id_ = response_id;
  this->cancel_timeout("direct-dialogue-window");
}

void GalileoAudioTap::trigger_all_(const std::vector<GalileoAudioTapTrigger *> &triggers) {
  for (auto *trigger : triggers) {
    if (trigger != nullptr)
      trigger->trigger();
  }
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

bool GalileoAudioTap::send_lifecycle_(const char *event) {
  if (event == nullptr)
    return false;
  const std::string response_id = std::string(event) == "capture_released" ? this->capture_response_id_ : this->direct_tts_response_id_;
  if (!valid_response_id(response_id) || !this->open_socket_())
    return false;
  std::array<uint8_t, HEADER_BYTES + 64> packet{};
  const std::string payload = std::string(event) + ":" + response_id;
  const size_t length = payload.size();
  std::memcpy(packet.data(), "GLA1", 4); packet[4] = 1; packet[5] = PACKET_LIFECYCLE;
  std::memcpy(packet.data() + 6, this->session_id_.data(), this->session_id_.size());
  const uint16_t payload_size = htons(static_cast<uint16_t>(length));
  std::memcpy(packet.data() + 22, &payload_size, sizeof(payload_size));
  std::memcpy(packet.data() + HEADER_BYTES, payload.data(), length);
  sockaddr_in destination{}; destination.sin_family = AF_INET; destination.sin_port = htons(this->port_);
  if (inet_aton(this->host_.c_str(), &destination.sin_addr) == 0) return false;
  return lwip_sendto(this->socket_, packet.data(), HEADER_BYTES + length, 0,
                     reinterpret_cast<sockaddr *>(&destination), sizeof(destination)) > 0;
}

bool GalileoAudioTap::open_socket_() {
  if (this->socket_ >= 0)
    return true;
  this->socket_ = lwip_socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if (this->socket_ < 0) {
    ESP_LOGW(TAG, "Unable to open UDP socket");
    return false;
  }
  sockaddr_in listener{};
  listener.sin_family = AF_INET;
  listener.sin_addr.s_addr = htonl(INADDR_ANY);
  listener.sin_port = htons(this->control_port_);
  if (lwip_bind(this->socket_, reinterpret_cast<sockaddr *>(&listener), sizeof(listener)) != 0) {
    ESP_LOGW(TAG, "Unable to bind direct-control port %u", this->control_port_);
    lwip_close(this->socket_);
    this->socket_ = -1;
    return false;
  }
  const int flags = fcntl(this->socket_, F_GETFL, 0);
  if (flags >= 0)
    fcntl(this->socket_, F_SETFL, flags | O_NONBLOCK);
  return true;
}

void GalileoAudioTap::poll_control_commands_() {
  if (this->socket_ < 0)
    return;
  std::array<uint8_t, MAX_CONTROL_BYTES> packet{};
  sockaddr_in source{};
  socklen_t source_size = sizeof(source);
  const int received = lwip_recvfrom(this->socket_, packet.data(), packet.size(), 0,
                                     reinterpret_cast<sockaddr *>(&source), &source_size);
  if (received < static_cast<int>(HEADER_BYTES) || std::memcmp(packet.data(), "GLA1", 4) != 0 || packet[4] != 1 ||
      std::memcmp(packet.data() + 6, this->session_id_.data(), this->session_id_.size()) != 0)
    return;
  const std::string payload(reinterpret_cast<const char *>(packet.data() + HEADER_BYTES),
                            static_cast<size_t>(received) - HEADER_BYTES);
  if (packet[5] == PACKET_ACTIVITY) {
    this->apply_remote_activity_(payload);
    return;
  }
  if (packet[5] == PACKET_DIALOGUE && payload.rfind("dialog_open:", 0) == 0) {
    const size_t separator = payload.find(':', 12);
    if (separator == std::string::npos)
      return;
    const int seconds = std::atoi(payload.substr(12, separator - 12).c_str());
    this->arm_dialogue_(static_cast<uint16_t>(seconds), payload.substr(separator + 1));
    ESP_LOGI(TAG, "Dialogue command received: %s", payload.c_str());
    return;
  }
  if (packet[5] != PACKET_TTS)
    return;
  const size_t separator = payload.find('\n');
  const std::string response_id = separator == std::string::npos ? "" : payload.substr(0, separator);
  const std::string url = separator == std::string::npos ? payload : payload.substr(separator + 1);
  if (!response_id.empty() && !valid_response_id(response_id)) {
    ESP_LOGW(TAG, "Rejected direct TTS response id");
    return;
  }
  if (url.empty() || url.size() > MAX_CONTROL_BYTES - HEADER_BYTES || url.rfind("http://", 0) != 0) {
    ESP_LOGW(TAG, "Rejected direct TTS datagram");
    return;
  }
  if (this->media_player_ == nullptr || !this->armed_)
    return;
  this->cancel_timeout("direct-tts-start");
  if (this->media_player_->state == media_player::MEDIA_PLAYER_STATE_IDLE) {
    this->start_direct_tts_(url, response_id);
  } else {
    this->media_player_->make_call().set_command(media_player::MEDIA_PLAYER_COMMAND_STOP).perform();
    this->set_timeout("direct-tts-start", 50, [this, url, response_id]() {
      this->start_direct_tts_when_idle_(url, response_id, 0);
    });
  }
}

void GalileoAudioTap::apply_remote_activity_(const std::string &activity) {
  // The Core may report only bounded, non-sensitive lifecycle failures.  Keep
  // the protocol closed: unknown strings cannot change the satellite state.
  if (activity != "error") {
    ESP_LOGW(TAG, "Rejected direct activity datagram");
    return;
  }
  this->trigger_all_(this->error_triggers_);
  ESP_LOGW(TAG, "Direct voice error reported by Core");
}

void GalileoAudioTap::on_microphone_data_(const std::vector<uint8_t> &data) {
  if (!this->capture_active_ || data.empty())
    return;

  const size_t frame_size = std::min(data.size(), MAX_PCM_BYTES);
  const size_t samples = frame_size / 2;
  // Do not let one noisy sample hold the endpoint detector open.  This ran
  // into the maximum capture time in a normal room because a single spike in
  // every microphone block was enough to count that whole block as speech.
  uint64_t total_magnitude = 0;
  for (size_t index = 0; index + 1 < frame_size; index += 2) {
    const int16_t sample = static_cast<int16_t>(static_cast<uint16_t>(data[index]) |
                                                (static_cast<uint16_t>(data[index + 1]) << 8));
    const uint16_t magnitude = sample == INT16_MIN ? UINT16_MAX : static_cast<uint16_t>(std::abs(sample));
    total_magnitude += magnitude;
  }
  const uint16_t magnitude = samples == 0 ? 0 : static_cast<uint16_t>(total_magnitude / samples);
  // The first 200 ms after a wake word is discarded as wake-word tail. It is
  // also a stable window to learn continuous background sound (for example a
  // radio) before the user starts their command.
  if (this->adaptive_noise_floor_ && this->captured_samples_ < 3200) {
    this->noise_floor_ = this->noise_floor_ == 0
                            ? magnitude
                            : static_cast<uint16_t>((this->noise_floor_ * 3U + magnitude) / 4U);
  }
  const uint32_t adaptive_threshold = this->adaptive_noise_floor_
                                          ? (static_cast<uint32_t>(this->noise_floor_) * this->noise_floor_ratio_percent_) / 100U
                                          : 0;
  const uint16_t endpoint_threshold = static_cast<uint16_t>(
      std::min<uint32_t>(UINT16_MAX, std::max<uint32_t>(this->silence_threshold_, adaptive_threshold)));
  const bool voiced = samples != 0 && magnitude >= endpoint_threshold;
  this->captured_samples_ += samples;
  if (voiced && this->captured_samples_ >= 3200) {  // Ignore the wake-word tail.
    this->speech_detected_ = true;
    this->silence_samples_ = 0;
  } else if (this->speech_detected_) {
    this->silence_samples_ += samples;
  }
  if (this->captured_samples_ >= this->maximum_capture_samples_ ||
      (this->speech_detected_ && this->silence_samples_ >= this->silence_samples_limit_)) {
    this->endpoint_detected_ = true;
  }
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
  if (!this->open_socket_())
    return;

  this->poll_control_commands_();
  if (!this->capture_active_)
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
  if (frame_size == 0) {
    if (this->endpoint_detected_)
      this->close_capture_(this->speech_detected_ ? "silence endpoint" : "maximum duration");
    return;
  }

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
  if (this->endpoint_detected_)
    this->close_capture_(this->speech_detected_ ? "silence endpoint" : "maximum duration");
}

}  // namespace esphome::galileo_audio_tap

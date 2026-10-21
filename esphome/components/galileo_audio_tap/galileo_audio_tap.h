#pragma once

#include <array>
#include <cstdint>
#include <string>
#include <vector>

#include "esphome/components/api/custom_api_device.h"
#include "esphome/components/microphone/microphone.h"
#include "esphome/core/component.h"

namespace esphome::galileo_audio_tap {

class GalileoAudioTap : public Component, public api::CustomAPIDevice {
 public:
  void set_microphone(microphone::Microphone *microphone) { this->microphone_ = microphone; }
  void set_host(const std::string &host) { this->host_ = host; }
  void set_port(uint16_t port) { this->port_ = port; }
  void set_session_id(const std::string &session_id);
  void set_enabled(bool enabled) { this->armed_ = enabled; }
  // Used only by the dedicated cutover profile after a local wake-word event.
  void start_capture_from_wake_word();
  void stop_capture_from_timeout();

  void setup() override;
  void loop() override;
  void dump_config() override;

 protected:
  static constexpr size_t MAX_PCM_BYTES = 1024;
  static constexpr size_t HEADER_BYTES = 24;
  static constexpr uint8_t PACKET_OPEN = 1;
  static constexpr uint8_t PACKET_PCM = 2;
  static constexpr uint8_t PACKET_CLOSE = 3;

  void on_microphone_data_(const std::vector<uint8_t> &data);
  bool open_socket_();
  bool send_control_(uint8_t packet_type);
  bool session_matches_(const std::string &provided) const;
  void start_capture(std::string session_id);
  void stop_capture(std::string session_id);

  microphone::Microphone *microphone_{nullptr};
  std::string host_;
  std::array<uint8_t, 8> session_id_{};
  uint16_t port_{0};
  bool armed_{false};
  bool capture_active_{false};
  int socket_{-1};
  uint32_t sequence_{0};
  uint32_t sample_offset_{0};
  uint32_t dropped_frames_{0};
  std::array<uint8_t, MAX_PCM_BYTES> pending_pcm_{};
  size_t pending_size_{0};
  portMUX_TYPE mutex_ = portMUX_INITIALIZER_UNLOCKED;
};

}  // namespace esphome::galileo_audio_tap

#pragma once

#include <array>
#include <cstdint>
#include <string>
#include <vector>

#include "esphome/components/api/custom_api_device.h"
#include "esphome/components/microphone/microphone.h"
#include "esphome/components/media_player/media_player.h"
#include "esphome/core/automation.h"
#include "esphome/core/component.h"

namespace esphome::galileo_audio_tap {

class GalileoAudioTapTrigger final : public Trigger<> {};

class GalileoAudioTap : public Component, public api::CustomAPIDevice {
 public:
  void set_microphone(microphone::Microphone *microphone) { this->microphone_ = microphone; }
  void set_host(const std::string &host) { this->host_ = host; }
  void set_port(uint16_t port) { this->port_ = port; }
  void set_control_port(uint16_t port) { this->control_port_ = port; }
  void set_session_id(const std::string &session_id);
  void set_enabled(bool enabled) { this->armed_ = enabled; }
  void set_media_player(media_player::MediaPlayer *media_player) { this->media_player_ = media_player; }
  void set_silence_threshold(uint16_t threshold) { this->silence_threshold_ = threshold; }
  void set_silence_ms(uint16_t duration_ms) { this->silence_samples_limit_ = duration_ms * 16U; }
  void set_maximum_capture_ms(uint16_t duration_ms) { this->maximum_capture_samples_ = duration_ms * 16U; }
  // Used only by the dedicated cutover profile after a local wake-word event.
  void start_capture_from_wake_word();
  void stop_capture_from_timeout();
  // Uses the announcement pipeline, separate from the active VoIP RX path.
  void play_direct_tts(std::string url);
  void register_capture_started_trigger(GalileoAudioTapTrigger *trigger) {
    this->capture_started_triggers_.push_back(trigger);
  }
  void register_capture_finished_trigger(GalileoAudioTapTrigger *trigger) {
    this->capture_finished_triggers_.push_back(trigger);
  }
  void register_tts_started_trigger(GalileoAudioTapTrigger *trigger) { this->tts_started_triggers_.push_back(trigger); }
  void register_tts_finished_trigger(GalileoAudioTapTrigger *trigger) { this->tts_finished_triggers_.push_back(trigger); }
  void register_error_trigger(GalileoAudioTapTrigger *trigger) { this->error_triggers_.push_back(trigger); }

  void setup() override;
  void loop() override;
  void dump_config() override;

 protected:
  static constexpr size_t MAX_PCM_BYTES = 1024;
  static constexpr size_t HEADER_BYTES = 24;
  static constexpr uint8_t PACKET_OPEN = 1;
  static constexpr uint8_t PACKET_PCM = 2;
  static constexpr uint8_t PACKET_CLOSE = 3;
  static constexpr uint8_t PACKET_TTS = 4;
  static constexpr uint8_t PACKET_ACTIVITY = 5;
  static constexpr size_t MAX_CONTROL_BYTES = 512;

  void on_microphone_data_(const std::vector<uint8_t> &data);
  bool open_socket_();
  bool send_control_(uint8_t packet_type);
  void poll_control_commands_();
  void apply_remote_activity_(const std::string &activity);
  bool session_matches_(const std::string &provided) const;
  void start_capture(std::string session_id);
  void stop_capture(std::string session_id);
  void reset_endpoint_detector_();
  void close_capture_(const char *reason);
  void finish_direct_tts_();
  static void trigger_all_(const std::vector<GalileoAudioTapTrigger *> &triggers);

  microphone::Microphone *microphone_{nullptr};
  media_player::MediaPlayer *media_player_{nullptr};
  std::string host_;
  std::array<uint8_t, 8> session_id_{};
  uint16_t port_{0};
  uint16_t control_port_{19008};
  bool armed_{false};
  bool capture_active_{false};
  int socket_{-1};
  uint32_t sequence_{0};
  uint32_t sample_offset_{0};
  uint32_t dropped_frames_{0};
  uint32_t captured_samples_{0};
  uint32_t silence_samples_{0};
  uint32_t silence_samples_limit_{19200};  // 1.2 seconds at 16 kHz
  uint32_t maximum_capture_samples_{240000};  // 15 seconds at 16 kHz
  uint16_t silence_threshold_{450};
  bool speech_detected_{false};
  volatile bool endpoint_detected_{false};
  bool direct_tts_pending_{false};
  bool direct_tts_announcing_{false};
  std::array<uint8_t, MAX_PCM_BYTES> pending_pcm_{};
  size_t pending_size_{0};
  portMUX_TYPE mutex_ = portMUX_INITIALIZER_UNLOCKED;
  std::vector<GalileoAudioTapTrigger *> capture_started_triggers_;
  std::vector<GalileoAudioTapTrigger *> capture_finished_triggers_;
  std::vector<GalileoAudioTapTrigger *> tts_started_triggers_;
  std::vector<GalileoAudioTapTrigger *> tts_finished_triggers_;
  std::vector<GalileoAudioTapTrigger *> error_triggers_;
};

}  // namespace esphome::galileo_audio_tap

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
  void set_dialogue_enabled(bool enabled) { this->dialogue_enabled_ = enabled; }
  // Follow-up answers: after a spoken question the Core may ask this speaker
  // to listen once more without the wake word ("listen:<response_id>").
  void set_followup_enabled(bool enabled) { this->followup_enabled_ = enabled; }
  void set_followup_maximum_capture_ms(uint16_t duration_ms) { this->followup_maximum_capture_samples_ = duration_ms * 16U; }
  void set_media_player(media_player::MediaPlayer *media_player) { this->media_player_ = media_player; }
  void set_silence_threshold(uint16_t threshold) { this->silence_threshold_ = threshold; }
  void set_adaptive_noise_floor(bool enabled) { this->adaptive_noise_floor_ = enabled; }
  void set_noise_floor_ratio(uint16_t ratio_percent) { this->noise_floor_ratio_percent_ = ratio_percent; }
  void set_silence_ms(uint16_t duration_ms) { this->silence_samples_limit_ = duration_ms * 16U; }
  void set_maximum_capture_ms(uint16_t duration_ms) { this->maximum_capture_samples_ = duration_ms * 16U; }
  // Audio kept from before the capture starts (16 kHz, 16-bit mono). The words
  // said right after the wake word fall while it is still being detected and
  // the cue plays; without this they never reach STT.
  void set_pre_roll_ms(uint16_t duration_ms) { this->pre_roll_bytes_ = duration_ms * 32U; }
  // Used only by the dedicated cutover profile after a local wake-word event.
  void start_capture_from_wake_word();
  void start_capture_from_dialogue_vad();
  // Called by on_followup_listen after its cue; opens the answer capture.
  void start_capture_for_followup();
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
  void register_followup_listen_trigger(GalileoAudioTapTrigger *trigger) {
    this->followup_listen_triggers_.push_back(trigger);
  }

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
  static constexpr uint8_t PACKET_DIALOGUE = 6;
  static constexpr uint8_t PACKET_LIFECYCLE = 7;
  static constexpr size_t MAX_CONTROL_BYTES = 512;

  void on_microphone_data_(const std::vector<uint8_t> &data);
  void remember_pre_roll_(const uint8_t *data, size_t size);
  void send_pre_roll_();
  bool send_pcm_(const uint8_t *data, size_t size);
  bool open_socket_();
  bool send_control_(uint8_t packet_type);
  bool send_lifecycle_(const char *event);
  void poll_control_commands_();
  void apply_remote_activity_(const std::string &activity);
  bool session_matches_(const std::string &provided) const;
  void start_capture(std::string session_id);
  void stop_capture(std::string session_id);
  void reset_endpoint_detector_();
  void close_capture_(const char *reason);
  void finish_direct_tts_();
  void start_direct_tts_(std::string url, std::string response_id = "");
  void start_direct_tts_when_idle_(std::string url, std::string response_id, uint8_t retries);
  void arm_dialogue_(uint16_t seconds, const std::string &response_id);
  void request_followup_(const std::string &response_id);
  bool open_live_capture_(bool with_pre_roll, uint32_t limit_samples);
  static void trigger_all_(const std::vector<GalileoAudioTapTrigger *> &triggers);

  microphone::Microphone *microphone_{nullptr};
  media_player::MediaPlayer *media_player_{nullptr};
  std::string host_;
  std::array<uint8_t, 8> session_id_{};
  uint16_t port_{0};
  uint16_t control_port_{19008};
  bool armed_{false};
  bool dialogue_enabled_{false};
  bool dialogue_pending_{false};
  bool dialogue_active_{false};
  uint16_t dialogue_seconds_{0};
  std::string dialogue_response_id_;
  std::string direct_tts_response_id_;
  std::string last_completed_response_id_;
  std::string capture_response_id_;
  bool followup_enabled_{false};
  bool followup_pending_{false};
  std::string followup_response_id_;
  uint32_t last_completed_at_{0};
  uint32_t followup_maximum_capture_samples_{112000};  // 7 seconds at 16 kHz
  uint32_t capture_limit_samples_{240000};
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
  bool adaptive_noise_floor_{false};
  uint16_t noise_floor_ratio_percent_{170};
  uint16_t noise_floor_{0};
  // Ambient level learned in the last wake-word capture. A follow-up answer
  // may start at once, so it reuses this instead of learning from the voice.
  uint16_t ambient_noise_floor_{0};
  bool followup_capture_{false};
  bool speech_detected_{false};
  volatile bool endpoint_detected_{false};
  bool direct_tts_pending_{false};
  bool direct_tts_announcing_{false};
  uint32_t direct_tts_started_at_{0};
  // Queue between the microphone task and loop(): one slot (16 ms) was not
  // enough, a slower loop() iteration dropped audio in the middle of words.
  static constexpr size_t QUEUE_SLOTS = 32;  // about half a second
  uint8_t *queue_{nullptr};
  std::array<uint16_t, QUEUE_SLOTS> queue_sizes_{};
  size_t queue_head_{0};
  size_t queue_count_{0};
  // Pre-roll ring buffer in PSRAM, written by the microphone task while idle.
  uint8_t *pre_roll_{nullptr};
  size_t pre_roll_bytes_{0};
  size_t pre_roll_head_{0};
  size_t pre_roll_fill_{0};
  portMUX_TYPE mutex_ = portMUX_INITIALIZER_UNLOCKED;
  std::vector<GalileoAudioTapTrigger *> capture_started_triggers_;
  std::vector<GalileoAudioTapTrigger *> capture_finished_triggers_;
  std::vector<GalileoAudioTapTrigger *> tts_started_triggers_;
  std::vector<GalileoAudioTapTrigger *> tts_finished_triggers_;
  std::vector<GalileoAudioTapTrigger *> error_triggers_;
  std::vector<GalileoAudioTapTrigger *> followup_listen_triggers_;
};

}  // namespace esphome::galileo_audio_tap

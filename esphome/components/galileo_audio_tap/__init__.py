"""A bounded, opt-in PCM tap used only by the Galileo direct-audio prototype."""

from esphome import automation
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import microphone, media_player
from esphome.const import CONF_ID, CONF_MICROPHONE, CONF_TRIGGER_ID


DEPENDENCIES = ["microphone"]

CONF_HOST = "host"
CONF_PORT = "port"
CONF_CONTROL_PORT = "control_port"
CONF_SESSION_ID = "session_id"
CONF_ENABLED = "enabled"
CONF_MEDIA_PLAYER = "media_player"
CONF_SILENCE_THRESHOLD = "silence_threshold"
CONF_ADAPTIVE_NOISE_FLOOR = "adaptive_noise_floor"
CONF_NOISE_FLOOR_RATIO = "noise_floor_ratio"
CONF_SILENCE_MS = "silence_ms"
CONF_MAXIMUM_CAPTURE_MS = "maximum_capture_ms"
CONF_ON_CAPTURE_STARTED = "on_capture_started"
CONF_ON_CAPTURE_FINISHED = "on_capture_finished"
CONF_ON_TTS_STARTED = "on_tts_started"
CONF_ON_TTS_FINISHED = "on_tts_finished"
CONF_ON_ERROR = "on_error"

galileo_audio_tap_ns = cg.esphome_ns.namespace("galileo_audio_tap")
GalileoAudioTap = galileo_audio_tap_ns.class_("GalileoAudioTap", cg.Component)
GalileoAudioTapTrigger = galileo_audio_tap_ns.class_("GalileoAudioTapTrigger", automation.Trigger.template())


def _automation_schema():
    return automation.validate_automation(
        {cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(GalileoAudioTapTrigger)}
    )


def validate_session_id(value):
    value = cv.string(value)
    if len(value) != 16 or any(char not in "0123456789abcdefABCDEF" for char in value):
        raise cv.Invalid("session_id must be exactly 16 hexadecimal characters")
    return value

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(GalileoAudioTap),
        cv.Required(CONF_MICROPHONE): cv.use_id(microphone.Microphone),
        cv.Required(CONF_HOST): cv.ipv4address,
        cv.Required(CONF_PORT): cv.port,
        cv.Optional(CONF_CONTROL_PORT, default=19008): cv.port,
        cv.Required(CONF_SESSION_ID): validate_session_id,
        cv.Optional(CONF_ENABLED, default=False): cv.boolean,
        cv.Optional(CONF_MEDIA_PLAYER): cv.use_id(media_player.MediaPlayer),
        cv.Optional(CONF_SILENCE_THRESHOLD, default=450): cv.int_range(min=1, max=32767),
        cv.Optional(CONF_ADAPTIVE_NOISE_FLOOR, default=False): cv.boolean,
        cv.Optional(CONF_NOISE_FLOOR_RATIO, default=170): cv.int_range(min=110, max=400),
        cv.Optional(CONF_SILENCE_MS, default=1200): cv.int_range(min=100, max=10000),
        cv.Optional(CONF_MAXIMUM_CAPTURE_MS, default=15000): cv.int_range(min=1000, max=30000),
        cv.Optional(CONF_ON_CAPTURE_STARTED): _automation_schema(),
        cv.Optional(CONF_ON_CAPTURE_FINISHED): _automation_schema(),
        cv.Optional(CONF_ON_TTS_STARTED): _automation_schema(),
        cv.Optional(CONF_ON_TTS_FINISHED): _automation_schema(),
        cv.Optional(CONF_ON_ERROR): _automation_schema(),
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    mic = await cg.get_variable(config[CONF_MICROPHONE])
    cg.add(var.set_microphone(mic))
    cg.add(var.set_host(str(config[CONF_HOST])))
    cg.add(var.set_port(config[CONF_PORT]))
    cg.add(var.set_control_port(config[CONF_CONTROL_PORT]))
    cg.add(var.set_session_id(config[CONF_SESSION_ID]))
    cg.add(var.set_enabled(config[CONF_ENABLED]))
    cg.add(var.set_silence_threshold(config[CONF_SILENCE_THRESHOLD]))
    cg.add(var.set_adaptive_noise_floor(config[CONF_ADAPTIVE_NOISE_FLOOR]))
    cg.add(var.set_noise_floor_ratio(config[CONF_NOISE_FLOOR_RATIO]))
    cg.add(var.set_silence_ms(config[CONF_SILENCE_MS]))
    cg.add(var.set_maximum_capture_ms(config[CONF_MAXIMUM_CAPTURE_MS]))
    if CONF_MEDIA_PLAYER in config:
        player = await cg.get_variable(config[CONF_MEDIA_PLAYER])
        cg.add(var.set_media_player(player))
    for key, register in (
        (CONF_ON_CAPTURE_STARTED, "register_capture_started_trigger"),
        (CONF_ON_CAPTURE_FINISHED, "register_capture_finished_trigger"),
        (CONF_ON_TTS_STARTED, "register_tts_started_trigger"),
        (CONF_ON_TTS_FINISHED, "register_tts_finished_trigger"),
        (CONF_ON_ERROR, "register_error_trigger"),
    ):
        for conf in config.get(key, []):
            trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID])
            cg.add(getattr(var, register)(trigger))
            await automation.build_automation(trigger, [], conf)

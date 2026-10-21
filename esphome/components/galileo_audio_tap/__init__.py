"""A bounded, opt-in PCM tap used only by the Galileo direct-audio prototype."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import microphone
from esphome.const import CONF_ID, CONF_MICROPHONE


DEPENDENCIES = ["microphone"]

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SESSION_ID = "session_id"
CONF_ENABLED = "enabled"

galileo_audio_tap_ns = cg.esphome_ns.namespace("galileo_audio_tap")
GalileoAudioTap = galileo_audio_tap_ns.class_("GalileoAudioTap", cg.Component)


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
        cv.Required(CONF_SESSION_ID): validate_session_id,
        cv.Optional(CONF_ENABLED, default=False): cv.boolean,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    mic = await cg.get_variable(config[CONF_MICROPHONE])
    cg.add(var.set_microphone(mic))
    cg.add(var.set_host(str(config[CONF_HOST])))
    cg.add(var.set_port(config[CONF_PORT]))
    cg.add(var.set_session_id(config[CONF_SESSION_ID]))
    cg.add(var.set_enabled(config[CONF_ENABLED]))

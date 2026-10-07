# Runtime validation - full AFE profile

Date: 2026-10-08

Firmware under test:

- `galileo-va-afe.yaml`
- ESPHome `2026.9.1`
- Build time shown by device: `2026-10-08 00:25:24 +0200`

## Result

PASS for current baseline.

The board booted, stayed on the network, initialized the full AFE audio path,
detected voice, started Home Assistant Assist, downloaded TTS audio and played
it back repeatedly without reset or safe mode.

## Runtime evidence

Observed after OTA rollback to the full AFE profile:

```text
tdm: total_slots=4 mic=0 mic2=2 tx_slot=0 reference=hardware ref_slot=1
processor: present=YES enabled=YES
voip_stack: Configured: SIP=udp/5060 RTP=40000 audio=full_duplex auto_answer=NO
```

Observed during live test:

```text
Voice Detected >> ON
Status LED >> ON, red, Spin
VA: tts_start
VA: tts_end
VA: end
audio_reader: Streaming ... .flac
media_player >> PLAYING
media_player >> IDLE
```

Three consecutive wake/Assist/TTS cycles completed without `stt-no-text-recognized`
or crash during the observed window.

## Memory snapshot after repeated TTS cycles

```text
Free Heap: 106243 B
Largest Free Block: 63488 B
Minimum Free Heap: 35832 B
Heap Fragmentation: 40.2 %
PSRAM Free: 4353648 B
Main Loop Max Time: 47 ms
CPU Frequency: 240 MHz
CPU Temperature: 51.5 C
WiFi Signal: 100 %
```

## Conclusion

This full AFE profile is the current working baseline. Do not change the audio
stack, pinout, AFE mode, VoIP/runtime packages or buffer strategy unless a new
test shows a concrete failure.

Next changes should be small and isolated:

1. wake word sensitivity only if Jarvis/Nabu regress;
2. diagnostic logging only if needed;
3. measured audio tests for distance, noise and barge-in.

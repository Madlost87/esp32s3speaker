# YAML non inclusi dalle casse (archiviati il 18/11/2026)

File spostati da `esphome/` perche' nessuna delle tre casse (Garage, Sala,
Taverna) li include, ne' direttamente ne' tramite altri pacchetti. Restano qui,
con lo stesso percorso relativo, per poterli recuperare.

Verifica fatta prima dello spostamento: la configurazione risolta
(`esphome config`) di `galileo-garage.yaml`, `galileo-sala.yaml` e
`galileo-va-direct-audio-cutover.yaml` e' identica prima e dopo, e il firmware
compilato ha lo stesso `config_hash` della release 2026.11.8.

Cosa contiene:

- profili Waveshare P4 / videocitofono (`voip/p4_*`, `voip/video_*`,
  `voip/waveshare_p4_touch_videophone_base.yaml`, `runtime/lvgl_ui_projection.yaml`);
- vecchi percorsi Assist/Home Assistant (`voip/ha_*`, `runtime/ha_connectivity.yaml`,
  `voice_assistant/*`), sostituiti dalla voce diretta e dai pacchetti upstream;
- copie locali di pacchetti upstream non usate (`voip/transport.yaml`,
  `voip/call_settings.yaml`, `voip/debug.yaml`, `voice_assistant/timers_runtime.yaml`,
  `voice_assistant/local_commands.yaml`): la base usa le versioni
  `github://n-IA-hane/esphome-intercom/...@<sha>`;
- doppioni del mute speaker (`voip/speaker_mute.yaml`,
  `voip/speaker_mute_runtime.yaml`): quello usato e' in
  `packages/satellite/controls.yaml`;
- `packages/status_ws2812_ring_galileo.yaml`: tema LED del vecchio profilo
  `galileo-va-afe.yaml` (vedi `docs/history/led-ring-theme.md`).

Aggiunto con la release 2026.11.9:
`components/galileo_direct_runtime/runtime_controller/timers.yaml`. Sono i
binding della funzione `timers` del runtime controller (suoneria dei timer di
Assist), tolta insieme al pacchetto upstream `timers_runtime.yaml`.

Per riusarne uno: riportarlo al suo percorso originale e correggere gli
`!include` relativi, che da qui non si risolvono.

# ESP32-S3 VoIP centralino

Data: 2026-10-08.

Questo repository contiene il firmware del satellite `Satellite Taverna`.
La configurazione VoIP e' nel profilo operativo `esphome/galileo-va-afe.yaml`.

## Ruolo del dispositivo

| Campo | Valore |
| --- | --- |
| Nome ESPHome | `galileo-va` |
| Friendly name | `Satellite Taverna` |
| IP osservato | `192.168.1.171` |
| Interno VoIP | `101` |
| SIP | `udp/5060` |
| RTP base | `40000/udp` |
| Gruppi squillo | `RG Casa`, `RG Tutti` |
| Conferenza | `CG Casa` |

Il dispositivo e' un peer SIP locale. Non registra un account SIP e non usa
digest authentication; la rubrica centrale e il routing sono gestiti da VoIP
Stack su Home Assistant.

## Configurazione aggiunta

Nel blocco `substitutions`:

- `voip_extension: "101"`;
- `voip_ring_groups: "RG Casa,RG Tutti"`;
- `voip_conference_groups: "CG Casa"`.

Nel blocco `voip_stack`:

- pubblicazione dell'interno `101`;
- appartenenza ai gruppi;
- contatti statici name-only per mantenere `Casa` come destinazione locale
  anche prima del push della rubrica HA.

I contatti statici non sostituiscono `sensor.voip_phonebook`: servono solo da
fallback di avvio/offline. Gli interni numerici e i gruppi vengono risolti dalla
rubrica centrale di Home Assistant.

## Architettura audio preservata

Non sono stati modificati pin, codec, AFE, buffer, media player, wake word,
Assist o pipeline audio. Il profilo resta quello validato:

- ES7210/ES8311 su TDM 48 kHz;
- AFE full-duplex con AEC/NS/SE;
- micro wake word e Assist;
- VoIP RX attraverso `voip_speaker_input`;
- TX dalla superficie `mic_main`.

## Validazione

Prima di compilare o caricare via OTA, verificare che i segreti locali non
siano placeholder:

```bash
python3 scripts/check_esphome_secrets.py
```

Il comando non stampa SSID o password; controlla solo che i valori siano
presenti e non contengano marker placeholder.

```bash
esphome config esphome/galileo-va-afe.yaml
esphome compile esphome/galileo-va-afe.yaml
```

Deploy OTA:

```bash
esphome upload esphome/galileo-va-afe.yaml --device 192.168.1.171
```

Log:

```bash
esphome logs esphome/galileo-va-afe.yaml --device 192.168.1.171
```

Verifiche attese nei log:

- endpoint VoIP con interno `101`;
- SIP `udp/5060`;
- RTP base `40000`;
- gruppi `RG Casa,RG Tutti` e `CG Casa`;
- audio `full_duplex`;
- nessuna regressione su wake/Assist/TTS.

## Test funzionali

1. ESP -> `Casa`: deve restare la chiamata gia' funzionante.
2. Browser -> `101`: il satellite deve squillare.
3. ESP -> `RG Casa`: deve far squillare Casa e il satellite quando applicabile.
4. ESP -> `RG Tutti`: oggi equivale ai membri presenti; `102` e `200` sono
   predisposti ma non testati.
5. Verificare risposta, rifiuto, occupato, hangup e audio bidirezionale.

## Rollback

Ripristinare la versione precedente del file e riflashare OTA:

```bash
git checkout HEAD~1 -- esphome/galileo-va-afe.yaml
esphome upload esphome/galileo-va-afe.yaml --device 192.168.1.171
```

## Stato deploy 2026-10-08

La configurazione e' stata validata e compilata con ESPHome 2026.9.1 tramite
Docker. L'OTA verso `192.168.1.171` e' stato completato con successo dal
protocollo OTA, ma dopo il riavvio il dispositivo non e' tornato raggiungibile
su `6053` o `5060`.

La causa trovata nel workspace locale e' `esphome/secrets.yaml` con valori
placeholder per `wifi_ssid` e `wifi_password`.

Recupero completato: dopo aver inserito credenziali Wi-Fi reali nel file locale
ignorato da Git, la board e' stata riflashata via USB seriale su
`/dev/ttyACM0`. Il flash e' stato verificato da `esptool` e il dispositivo e'
tornato raggiungibile su:

- `192.168.1.171:6053` per ESPHome API;
- `192.168.1.171:5060` per SIP VoIP Stack.

I log ESPHome post-flash confermano boot ESPHome 2026.9.1, audio stack attivo,
SIP configurato su UDP `5060`, segnale Wi-Fi `100%` e VAD funzionante.

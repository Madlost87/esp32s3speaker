# ESP32-S3 VoIP centralino

Data: 2026-10-08.

Questo repository contiene il firmware del satellite `Satellite Taverna`.
La configurazione VoIP e' nel profilo operativo `esphome/galileo-va-afe.yaml`.

Questa guida copre solo il lato ESP32-S3. La rubrica centrale, la dashboard,
gli interni e il provisioning Home Assistant sono documentati nell'altro repo:
`/home/denny/progerttidenny/galileovianicolini/homeassistant/docs/voip-centralino.md`.

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

## Identita' e nomi

`galileo-va` e' l'identita' tecnica stabile del nodo ESPHome. Va mantenuta per
non creare un secondo device in Home Assistant, non perdere le entity esistenti
e continuare a usare lo stesso host mDNS/build cache.

`Satellite Taverna` e' invece il nome umano mostrato in Home Assistant, nella
rubrica VoIP e nei test di chiamata. Anche se il SIP URI resta
`sip:galileo-va@192.168.1.171;transport=udp`, la chiamata deve risultare verso
`Satellite Taverna`.

I vecchi profili sperimentali nella cartella `esphome/` possono ancora avere
nomi `Galileo Voice...`: non sono il profilo operativo. Il profilo operativo e'
solo `esphome/galileo-va-afe.yaml`.

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

### Comandi Docker usati nel setup locale

Nel workspace di questo repository e' stato usato ESPHome via Docker:

```bash
cd /home/denny/progerttidenny/galileovianicolini/speakersatellite/esp32-s3-audio-docs

docker run --rm --network host --user 1000:1000 --group-add 986 \
  -e USER=denny -e LOGNAME=denny -e HOME=/config -e UV_CACHE_DIR=/config/.cache/uv \
  -v "$PWD/esphome:/config" \
  ghcr.io/esphome/esphome:2026.9.1 \
  config /config/galileo-va-afe.yaml
```

OTA su rete:

```bash
docker run --rm --network host --user 1000:1000 --group-add 986 \
  -e USER=denny -e LOGNAME=denny -e HOME=/config -e UV_CACHE_DIR=/config/.cache/uv \
  -v "$PWD/esphome:/config" \
  ghcr.io/esphome/esphome:2026.9.1 \
  run /config/galileo-va-afe.yaml --device 192.168.1.171
```

Flash USB di recupero:

```bash
docker run --rm --network host --user 1000:1000 --group-add 986 \
  -e USER=denny -e LOGNAME=denny -e HOME=/config -e UV_CACHE_DIR=/config/.cache/uv \
  -v "$PWD/esphome:/config" \
  --device /dev/ttyACM0 \
  ghcr.io/esphome/esphome:2026.9.1 \
  run /config/galileo-va-afe.yaml --device /dev/ttyACM0
```

Se si cambia solo documentazione o rubrica HA non serve riflashare l'ESP. Se si
cambia `friendly_name`, `voip_extension`, pin/audio o pacchetti ESPHome, serve
ricompilare e caricare OTA.

## Test funzionali

1. ESP -> `Casa`: deve restare la chiamata gia' funzionante.
2. Browser -> `101`: il satellite deve squillare.
3. ESP -> `RG Casa`: deve far squillare Casa e il satellite quando applicabile.
4. ESP -> `RG Tutti`: oggi equivale ai membri presenti; `102` e `200` sono
   predisposti ma non testati.
5. Verificare risposta, rifiuto, occupato, hangup e audio bidirezionale.

## Tasti fisici

La board ha cinque tasti visibili, ma nel profilo operativo sono cablati questi
controlli:

| Tasto | Entity / pin logico | Azione VoIP |
| --- | --- | --- |
| Boot | `GPIO0` | sequenze multi-click per controlli runtime/mute, non e' il tasto chiamata principale |
| Key 1 | TCA9555 EXIO `9` | `voip_stack.call_toggle` |
| Key 2 | TCA9555 EXIO `10` | contatto successivo |
| Key 3 | TCA9555 EXIO `11` | contatto precedente, oppure rifiuta se sta squillando |

Per un test senza toccare la board si puo' usare Home Assistant: chiamare `101`
dal browser phone o dal servizio `voip_stack.call`.

## Rollback

Ripristinare la versione precedente del file e riflashare OTA:

```bash
git checkout HEAD~1 -- esphome/galileo-va-afe.yaml
esphome upload esphome/galileo-va-afe.yaml --device 192.168.1.171
```

## Stato deploy 2026-10-08

La configurazione e' stata validata, compilata e caricata con ESPHome 2026.9.1
tramite Docker.

Durante il primo deploy del progetto VoIP era stato necessario un recupero USB:
il file locale `esphome/secrets.yaml` conteneva placeholder Wi-Fi e l'ESP non
era tornato in rete dopo OTA. Dopo aver inserito credenziali Wi-Fi reali, la
board e' stata riflashata via USB seriale su `/dev/ttyACM0`.

Stato finale verificato dopo il rename a `Satellite Taverna`:

- `192.168.1.171:6053` per ESPHome API;
- `192.168.1.171:5060` per SIP VoIP Stack.

L'ultimo OTA pulito ha prodotto build time `2026-10-08 21:05:14 +0000`,
`friendly_name: Satellite Taverna`, SIP configurato su UDP `5060`, rubrica
ricevuta da Home Assistant e contatto iniziale `Casa`.

Test centralino eseguito: Home Assistant `Casa` ha chiamato l'interno `101`.
VoIP Stack ha generato INVITE verso
`sip:galileo-va@192.168.1.171;transport=udp`, ha ricevuto SIP `180 Ringing` e
la chiamata e' stata chiusa manualmente tornando a `idle`.

## Regole operative

- Non esporre `5060/udp` o RTP del satellite su Internet.
- Per test fuori casa usare VPN verso la LAN e poi softphone/HA.
- Non salvare token Home Assistant in questo repository.
- `ESP Cucina` e `Softphone 200` sono predisposizioni della rubrica HA, non
  dispositivi ESP attivi in questo repository.

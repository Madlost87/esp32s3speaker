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

## Inventario hardware/software della cassa

Riepilogo del satellite `192.168.1.171`, utile per capire cosa e' gia' usato e
cosa e' solo predisposto.

### Hardware usato

| Componente | Stato | Note |
| --- | --- | --- |
| Board Waveshare ESP32-S3-AUDIO-Board | usata | satellite principale `Satellite Taverna` |
| ESP32-S3 dual core | usato | target ESP-IDF, Wi-Fi e runtime audio/VoIP |
| Flash 16 MB | usata | firmware ESPHome, OTA e partizioni app |
| PSRAM 8 MB octal | usata | buffer audio, task stack e componenti pesanti |
| ES7210 ADC dual mic | usato | due microfoni su TDM |
| ES8311 DAC | usato | uscita speaker e reference audio |
| NS4150 mono 3 W | usato | amplificatore speaker |
| Speaker integrato | usato | TTS, media, ringtone, VoIP RX |
| WS2812 status ring | usato | 7 LED su `GPIO38` |
| TCA9555 I/O expander | usato | tasti fisici e speaker enable |
| Key 1 | usato | chiamata/hangup |
| Key 2 | usato | prossimo contatto |
| Key 3 | usato | contatto precedente o rifiuto se squilla |
| BOOT `GPIO0` | usato | controlli runtime/mute tramite sequenze |
| Batteria/charger board | non validato | hardware presente, non documentato come alimentazione operativa |

### Pin e bus

| Funzione | Pin |
| --- | --- |
| I2S MCLK | `GPIO12` |
| I2S BCLK | `GPIO13` |
| I2S LRCLK | `GPIO14` |
| I2S DIN | `GPIO15` |
| I2S DOUT | `GPIO16` |
| I2C SDA | `GPIO11` |
| I2C SCL | `GPIO10` |
| LED WS2812 | `GPIO38` |
| BOOT | `GPIO0` |

TDM verificato su questa board:

- slot `0`: microfono destro;
- slot `2`: microfono sinistro;
- slot `1`: reference playback per AEC;
- slot `3`: inutilizzato/quasi silente.

### Stack audio usato

- audio full duplex;
- ES7210/ES8311 a 48 kHz;
- AFE con AEC, noise suppression, speech enhancement e VAD;
- micro wake word e Assist ancora presenti nel profilo;
- `mic_main` come sorgente VoIP TX;
- `voip_speaker_input` come destinazione VoIP RX;
- mixer/resampler condivisi per media, TTS, annunci e chiamate;
- ringtone e timer attraverso pipeline audio locale.

### Software e servizi

| Elemento | Valore |
| --- | --- |
| ESPHome | `2026.9.1` |
| ESP-IDF | `5.5.5` |
| Profilo operativo | `esphome/galileo-va-afe.yaml` |
| Nome tecnico | `galileo-va` |
| Nome umano | `Satellite Taverna` |
| IP attuale | `192.168.1.171` |
| ESPHome API | TCP `6053` |
| SIP | UDP `5060` |
| RTP base | UDP `40000` |
| Interno | `101` |
| Gruppi | `RG Casa`, `RG Tutti`, `CG Casa` |

Componenti principali:

- `voip_stack`;
- `esp_audio_stack`;
- `esp_afe`;
- `micro_wake_word`;
- `voice_assistant`;
- `runtime_controller`;
- `sendspin`;
- mixer/resampler/media player ESPHome;
- diagnostica audio e VoIP.

### Funzioni gia' validate

- OTA via rete;
- recovery USB su `/dev/ttyACM0`;
- ESPHome API raggiungibile su `6053`;
- SIP raggiungibile su `5060`;
- chiamata Home Assistant `Casa` -> interno `101`;
- risposta SIP `180 Ringing`;
- ritorno a `idle` dopo hangup controllato;
- ricezione rubrica da Home Assistant;
- destinazione iniziale `Casa`;
- audio stack attivo e VAD funzionante nei log.

### Predisposto ma non ancora completato

- `ESP Cucina`: solo placeholder rubrica;
- `Softphone 200`: predisposto, account non ancora attivato;
- SIP trunk/provider esterno;
- comandi vocali per chiamare/rispondere/chiudere;
- auto-answer da trunk con whitelist;
- uso in ufficio/rete diversa;
- secondo satellite fisico.

### Non usato

- Asterisk/FreePBX;
- registrazione SIP dell'ESP;
- numero VoIP pubblico;
- token Home Assistant salvati sull'ESP;
- esposizione SIP/RTP su Internet.

In sintesi: la board audio e' sfruttata nelle parti importanti per il caso
d'uso attuale, cioe' microfoni, speaker, codec, AEC, LED, tasti, Wi-Fi,
ESPHome API e SIP/RTP. Le evoluzioni ancora aperte sono soprattutto lato
centralino, provider SIP, automazioni e sicurezza.

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

## Dove customizzare il lato ESP

Le personalizzazioni operative stanno quasi tutte in
`esphome/galileo-va-afe.yaml`, nel blocco `substitutions`.

| Cosa vuoi cambiare | Dove | Serve OTA? | Note |
| --- | --- | --- | --- |
| Nome tecnico ESPHome/mDNS | `substitutions.name` | si | Cambiarlo crea un nuovo device HA. Per `Satellite Taverna` resta `galileo-va`. |
| Nome umano | `substitutions.friendly_name` | si | Visibile in HA; va allineato anche nella rubrica del repo HA. |
| Interno VoIP | `substitutions.voip_extension` | si | Deve essere unico e presente in `voip/phonebook.json` nell'altro repo. |
| Gruppi squillo | `substitutions.voip_ring_groups` | si | Lista separata da virgole, per esempio `RG Casa,RG Tutti`. |
| Gruppi conferenza | `substitutions.voip_conference_groups` | si | Lista separata da virgole, per esempio `CG Casa`. |
| Componenti ESPHome esterni | `*_components_source` | si | Cambiare solo se vuoi provare fork o versioni pin. |
| Asset remoti audio/UI | `assets_base` | si | Usare URL stabile; non mettere token nell'URL se il repo e' pubblico. |
| Pin codec/I2S/LED/tasti | substitutions pinout e blocchi hardware | si | Cambiare solo con schema board verificato. |
| Wi-Fi | `esphome/secrets.yaml` locale | si | File ignorato da Git: non committare SSID/password. |
| IP del dispositivo | DHCP reservation/router o `wifi.manual_ip` se aggiunto | forse | Preferita reservation sul router. Se aggiungi `manual_ip`, serve OTA/USB. |

Il blocco `voip_stack.static_contacts` contiene fallback locali name-only:
`Casa`, `RG Casa`, `RG Tutti`, `ESP Cucina`, `Softphone 200`. Se cambi i nomi
dei contatti o gruppi nel repo HA, aggiorna anche questa lista per mantenere il
cycler hardware coerente durante l'avvio.

## Cambio Home Assistant o centralino

L'ESP non salva token Home Assistant e non conosce direttamente
`HA_TOKEN`. Riceve la rubrica da Home Assistant tramite integrazione ESPHome/API
e parla SIP/RTP verso i peer indicati da VoIP Stack.

Se cambi host Home Assistant, Raspberry o centralino:

1. Aggiorna la rubrica nel repo HA: IP `home_assistant_host`, contatti,
   gruppi e script di provisioning.
2. Assicurati che il nuovo HA veda l'ESP via ESPHome API su `6053`.
3. Assicurati che il nuovo HA possa raggiungere SIP dell'ESP su
   `192.168.1.171:5060/udp` o sul nuovo IP.
4. Applica la rubrica da Home Assistant con `provision_voip_stack.py`.
5. Rifai un test `Casa` -> `101` e un test ESP -> `Casa`.

Non serve cambiare firmware ESP se sposti solo Home Assistant ma mantieni:

- stesso interno `101`;
- stessi nomi gruppo;
- stesso IP ESP;
- stesso schema SIP/RTP.

Serve invece OTA se cambi identita' ESP, interno, gruppi pubblicati, pin,
componenti o Wi-Fi.

## Endpoint, chiavi e segreti

Questo repo non deve contenere segreti runtime. Regole:

- Wi-Fi solo in `esphome/secrets.yaml`, ignorato da Git.
- Token Home Assistant solo in shell temporanea nel repo HA, mai qui.
- Password softphone/SIP trunk solo in variabili ambiente o password manager.
- API key o endpoint privati di servizi esterni non vanno messi nei pacchetti
  ESPHome o in URL pubblici.

Se un componente futuro richiede API key lato ESP, preferire una secret locale:

```yaml
api_key: !secret nome_servizio_api_key
```

e aggiungere solo un placeholder in `esphome/secrets.example.yaml`, non il
valore reale.

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

## Prossimi passi

Roadmap lato ESP/satelliti:

1. Mantenere `Satellite Taverna` come baseline stabile.
   - Non cambiare `name: galileo-va` salvo migrazione intenzionale.
   - Usare questo profilo come riferimento per audio, tasti, LED e VoIP.
2. Testare meglio i controlli fisici.
   - Key 1: chiamata/hangup.
   - Key 2/Key 3: cambio contatto e rifiuto chiamata.
   - Verificare comportamento durante squillo, occupato e chiamata attiva.
3. Preparare la prova in ufficio.
   - Opzione consigliata: usare un travel router che crea una LAN stabile per
     Raspberry ed ESP, mantenendo gli IP attuali.
   - Alternativa: aggiungere la Wi-Fi ufficio come seconda rete ESPHome in
     `wifi.networks`, senza rimuovere la rete di casa.
   - Salvare SSID/password ufficio solo in `esphome/secrets.yaml`, mai in Git.
   - Fare OTA a casa prima della prova, per evitare recovery USB in ufficio.
   - Se in ufficio gli IP cambiano, aggiornare il repo Home Assistant e
     rieseguire il provisioning rubrica.
4. Preparare un eventuale secondo satellite.
   - Duplicare il profilo operativo solo quando esiste il nuovo hardware.
   - Usare un `name` unico, per esempio `esp-cucina`.
   - Usare un interno unico, per esempio `102`.
   - Aggiornare anche `phonebook.json` nel repo Home Assistant.
5. Rendere reale `ESP Cucina` solo dopo flash e test.
   - Oggi `ESP Cucina` e' solo un placeholder della rubrica.
   - Quando il device esiste, impostare IP stabile e testare SIP/RTP.
6. Preparare il futuro SIP trunk.
   - Il trunk e' un lavoro lato Home Assistant/provider, non lato firmware ESP.
   - Non serve OTA se `Satellite Taverna` resta interno `101` nei gruppi locali.
   - Serve OTA solo se si cambia interno, nome pubblicato, gruppi o comportamento
     chiamata del satellite.
   - Dopo l'attivazione trunk, testare inbound provider -> `RG Casa` e verificare
     che il satellite squilli correttamente.
7. Valutare comandi vocali e auto-answer.
   - La chiamata vocale parte da Home Assistant/Assist, non dal firmware puro.
   - Risposta/rifiuto vocali durante squillo vanno testati per interferenze tra
     ringtone, wake word, microfono e VoIP.
   - Auto-answer da trunk deve essere deciso lato Home Assistant con whitelist;
     l'ESP deve solo comportarsi bene come endpoint audio.
   - Non usare il satellite come unico sistema di emergenza.
8. Hardening firmware.
   - Tenere `esphome/secrets.yaml` fuori da Git.
   - Pin delle dipendenze esterne solo se serve stabilizzare una release.
   - Documentare ogni cambio audio/pin prima di OTA.
9. Test regressione dopo ogni OTA.
   - `6053` aperta.
   - `5060/udp` aperta.
   - chiamata HA -> `101`.
   - chiamata ESP -> `Casa`.
   - audio bidirezionale.

## Regole operative

- Non esporre `5060/udp` o RTP del satellite su Internet.
- Per test fuori casa usare VPN verso la LAN e poi softphone/HA.
- Non salvare token Home Assistant in questo repository.
- `ESP Cucina` e `Softphone 200` sono predisposizioni della rubrica HA, non
  dispositivi ESP attivi in questo repository.

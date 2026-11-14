# Flotta satelliti: un fix, tutte le casse

Come si lavora su una cassa sola e poi si porta lo stesso firmware su tutte,
come si aggiunge una cassa nuova e come si replica il sistema in un'altra casa.

Stato attuale delle casse e build installate: [satellites.md](satellites.md).

## Idea in breve

- **Un solo firmware.** Tutte le casse compilano la stessa base. Un fix si fa
  una volta sola, nella base.
- **Una release, un numero.** La base dichiara `firmware_release`, per esempio
  `2026.11.1`. Ogni cassa la mostra in Home Assistant, nell'entita' diagnostica
  *Firmware Release* e nelle informazioni del dispositivo.
- **Un canarino.** Il rollout aggiorna prima una cassa sola (oggi il Garage), si
  ferma per il test a voce e solo dopo passa alle altre.
- **Un controllo dopo ogni OTA.** Lo script verifica che la cassa sia tornata
  online con la release giusta, VoIP `idle`, wake word accesa e IP corretto. Se
  il controllo fallisce, reinstalla la build precedente e si ferma.
- **Uno storico.** Ogni build resta archiviata con il suo hash, quindi qualsiasi
  cassa puo' tornare indietro di una o piu' release.

## I tre livelli della configurazione

| Livello | File | Contiene | Cambia quando |
| --- | --- | --- | --- |
| Firmware | `esphome/galileo-va-direct-audio-cutover-base.yaml` | hardware, audio, AFE, wake word, VoIP, versioni dei componenti esterni, `firmware_release` | si fa un fix o un upgrade |
| Sito | `esphome/sites/casa.yaml` | IP di Galileo Core, gateway, DNS, Wi-Fi (`!secret`), gruppi VoIP | cambia la rete o la casa |
| Dispositivo | `esphome/galileo-sala.yaml` (uno per cassa) | nome, nome visibile, IP statico, interno, porte UDP, segreto di sessione | si aggiunge o si sposta una cassa |

Regola: nei file dispositivo **non** si mette comportamento. Se serve una
differenza (per esempio una cassa con un altro microfono), la si aggiunge alla
base come sostituzione con un valore predefinito e la si sovrascrive solo li'.

I file dispositivo restano nella cartella `esphome/` (non in sottocartelle):
ESPHome risolve componenti locali e cartelle di build rispetto a quella
cartella, e l'ESPHome Device Builder li vede solo li'. I nomi dei file sono
storici (`galileo-va-direct-audio-cutover.yaml` e' Taverna) e non vanno
rinominati senza un piano: il nome ESPHome definisce il dispositivo in Home
Assistant.

Gli altri profili in `esphome/` (`galileo-va-afe*.yaml`, `galileo-va.yaml`,
`galileo-va-direct-audio-test.yaml`) sono di laboratorio o di recovery: non
fanno parte della flotta e lo script non li tocca.

## Strumenti

```text
fleet/casa.yaml              inventario: quali casse, ordine di rollout, canarino
fleet/casa.installed.json    stato installato per cassa (release, hash, storico)
tools/fleet                  wrapper: usa il Python del toolchain ESPHome
tools/fleet.py               lo script
~/esp-firmware-builds/casa/<release>/   binari archiviati (fuori da Git)
```

L'inventario non ripete IP, interni e porte: lo script li legge dai file
dispositivo, cosi' non possono divergere.

I binari stanno fuori da Git perche' contengono le credenziali Wi-Fi. Per ogni
release ci sono `<cassa>.ota.bin`, `<cassa>.factory.bin`, il log di
compilazione, `build.json` (commit, `config_hash`, `build_time`, hash) e
`SHA256SUMS`. La cartella `pre-2026.11.1/` contiene le build installate il
14/11/2026, prima del sistema flotta.

Comandi:

```bash
tools/fleet status                 # stato live di tutte le casse
tools/fleet status sala            # una sola
tools/fleet release 2026.11.2      # nuova release nella base
tools/fleet build                  # compila e archivia tutte le casse
tools/fleet rollout                # canarino, pausa, poi le altre
tools/fleet rollout sala           # solo alcune casse
tools/fleet rollback sala          # torna alla build precedente
tools/fleet rollback sala --to 2026.11.1
tools/fleet docs                   # rigenera la tabella in satellites.md
tools/fleet new cucina --ip 192.168.1.173 --area "Cucina 1" --phonebook
```

## Ciclo di un fix o di un upgrade

1. **Sviluppo su una cassa.** Modificare la base (o un componente) e provarla su
   una cassa sola, senza toccare le altre:
   ```bash
   cd esphome
   esphome run galileo-garage-hybrid.yaml --device 192.168.1.133
   ```
   Si possono fare tutte le prove necessarie. La cassa dichiarera' ancora la
   release precedente perche' il numero non e' stato cambiato, ma
   `fleet status` la segnala con "build diversa da quella registrata". La
   segnalazione sparisce al rollout successivo o dopo un `fleet rollback`.

2. **Componenti esterni.** Se il fix e' in un componente esterno (`n-IA-hane/*`),
   per le prove si puo' puntare temporaneamente a un branch o a una cartella
   locale. Prima della release si fissa di nuovo uno SHA in
   `substitutions` e negli URL `github://...@<sha>` della base: mai branch o tag
   mobili in una release.

3. **Release.** Quando la prova e' buona:
   ```bash
   tools/fleet release 2026.11.2
   git commit -am "Release firmware 2026.11.2: <cosa cambia>"
   git tag fw-2026.11.2
   ```

4. **Build.** `tools/fleet build` compila tutte le casse dal commit pulito e
   archivia i binari. Rifiuta di partire se `esphome/` ha modifiche non
   committate. Con `--allow-dirty` si fa una build di prova, archiviata in
   `<release>-dev/`, che il rollout non usa.

5. **Rollout.** `tools/fleet rollout` procede cosi':
   - controlla che ogni binario esista e abbia l'hash registrato;
   - aggiorna il canarino e verifica il controllo di salute;
   - si ferma e chiede il test a voce: wake word, "che ore sono", una chiamata;
   - con Invio prosegue con le altre casse nell'ordine dell'inventario.

   Le casse gia' sulla release vengono saltate, salvo `--force`. Al primo
   controllo fallito ripristina la build precedente su quella cassa e si ferma
   senza toccare le successive.

6. **Registrazione.** Lo script aggiorna `fleet/casa.installed.json` e la
   tabella in `satellites.md`. Committarli:
   ```bash
   git add fleet/casa.installed.json docs/satellites.md
   git commit -m "Rollout firmware 2026.11.2"
   ```

Formato delle release: `AAAA.M.N`, per esempio `2026.11.2` (anno, mese,
progressivo). Ogni release ha un tag Git `fw-<release>` sul commit compilato.

## Controllo di salute

Dopo un OTA lo script attende il riavvio, fino a 4 minuti, e legge via API
ESPHome:

| Controllo | Atteso |
| --- | --- |
| Nome del dispositivo | uguale al file dispositivo |
| `project_version` | la release appena installata |
| `voip_state` | `idle` |
| `voip_endpoint` | contiene l'IP statico della cassa |
| Switch `wake_word` | acceso |

Il controllo automatico non sostituisce il test a voce sul canarino: verifica
che la cassa sia viva e configurata, non che senta e parli bene.

## Rollback

```bash
tools/fleet rollback taverna                 # build precedente
tools/fleet rollback taverna --to 2026.11.1  # una release precedente specifica
```

Lo storico tiene le ultime 5 build per cassa. Se lo script non e' disponibile,
si puo' fare a mano:

```bash
cd esphome
esphome upload galileo-va-direct-audio-cutover.yaml --device 192.168.1.171 \
  --file ~/esp-firmware-builds/casa/2026.11.1/taverna.ota.bin
```

Se una cassa non si avvia piu' (bootloop), serve il cavo USB e il binario
`factory`:

```bash
esphome upload <profilo> --device /dev/ttyACM0 --file ~/esp-firmware-builds/casa/<release>/<cassa>.factory.bin
```

Il recovery completo e' in [golden-firmware-recovery.md](golden-firmware-recovery.md).

## Aggiungere una cassa

```bash
tools/fleet new cucina --ip 192.168.1.173 --area "Cucina 1" --phonebook
```

Lo script fa da solo queste cose:

- assegna l'interno successivo (oggi `104`) e le porte UDP successive (due
  per cassa, in sequenza da `19007`). Salta `19013`, riservata in Galileo Core
  alla discovery delle casse (Spec 017), quindi la prossima coppia e'
  `19015`/`19016`;
- crea `esphome/satellite-cucina.yaml` dal modello;
- genera il segreto di sessione in `esphome/secrets.yaml` (non versionato);
- aggiunge la cassa in fondo a `fleet/casa.yaml`;
- con `--phonebook`, aggiunge l'interno a `homeassistant/voip/phonebook.json`
  e ai gruppi del sito.

Restano a mano, nell'ordine:

1. **Router:** riservare l'IP al MAC della scheda.
2. **Primo flash via USB** (gli OTA funzionano solo dopo il primo flash):
   ```bash
   cd esphome && esphome run satellite-cucina.yaml --device /dev/ttyACM0
   ```
   Prima di sovrascrivere una board di fabbrica, fare il backup della flash
   come in [first_flash_checklist.md](first_flash_checklist.md).
3. **Galileo Core:** aggiungere la riga stampata dallo script a
   `GALILEO_DIRECT_VOICE_SATELLITES_JSON` nel `.env` di Galileo Core sul
   Raspberry. Il `session_id` va copiato da `secrets.yaml`. `ha_entity` e'
   l'entita' `assist_satellite.*` della cassa in Home Assistant, nota dopo il
   punto 4: da' a Core la stanza della cassa, che comandera' per default i
   dispositivi di quell'area ([comandi per stanza](../../../homeassistant/docs/operations/comandi-vocali-stanze.md)
   nel repository Home Assistant). Poi riavviare il container.
4. **Home Assistant:**
   - adottare il dispositivo ESPHome e assegnarlo all'area;
   - aggiungerlo alle dashboard Casa, Voce e Sistema;
   - aggiungere il suo pulsante "Test voce" in
     `ha_config/packages/satelliti/satelliti_test_voce.yaml`: premuto, la cassa
     dice nome e stanza, e conferma cosi' che l'area sia giusta;
   - copiare la rubrica aggiornata sul Raspberry. Il roster VoIP live si
     costruisce da solo dai dispositivi ESPHome; `phonebook.json` serve come
     documentazione e provisioning.
5. **Verifica:**
   - `tools/fleet status cucina` deve mostrare la release corrente, VoIP `idle`
     e wake word `on`;
   - il pulsante Test voce in Home Assistant fa dire alla cassa il suo nome e
     la stanza giusta;
   - provare a voce e con una chiamata da un'altra cassa.
6. **Commit** dei due repository, firmware e Home Assistant.

## Un'altra casa (nuovo sito)

Il firmware non contiene niente di specifico della casa: la casa sta nel
livello sito. Per un'installazione nuova:

1. **Sito:** creare `esphome/sites/<sito>.yaml` con le stesse chiavi di
   `sites/casa.yaml`:
   - IP di Galileo Core e rete;
   - gruppi VoIP;
   - segreti Wi-Fi con nomi propri del sito (`!secret <sito>_wifi_ssid`), da
     aggiungere a `secrets.yaml`.
2. **Inventario:** creare `fleet/<sito>.yaml`, con i suoi `state_file` e
   `artifacts_dir`, e i file dispositivo che includono `sites/<sito>.yaml`.
   I nomi ESPHome devono essere unici tra tutti i siti, perche' condividono la
   cartella `esphome/`.
3. **Comandi:** usare `--site`:
   ```bash
   tools/fleet --site <sito> new soggiorno --ip 10.0.0.50 --area Soggiorno
   tools/fleet --site <sito> build
   tools/fleet --site <sito> rollout
   ```

La stessa release vale per tutti i siti: un fix compilato una volta si
distribuisce sito per sito, ciascuno con il suo canarino.

Dal lato server servono Home Assistant e Galileo Core per il nuovo sito:

| Componente | Riferimento |
| --- | --- |
| Configurazione di Home Assistant | repository `homeassistant` (`docs/operations/home-assistant-config.md`) |
| Galileo Core | `GALILEO_DIRECT_VOICE_SATELLITES_JSON` con le casse del sito |
| Rubrica VoIP | `phonebook.json` del sito |

## Limiti noti

- Le build girano sul PC di sviluppo, dove c'e' il toolchain ESPHome. Sul
  Raspberry la compilazione sarebbe molto lenta.
- Le build precedenti al sistema flotta non dichiarano la release: `status`
  mostra `-` finche' la cassa non riceve la prima release `2026.11.1`.
- Il controllo di salute non prova l'audio. Il test a voce sul canarino resta
  obbligatorio.
- La compilazione puo' bloccarsi nel download dei componenti ESP-IDF, come e'
  successo il 14/11. Lo script interrompe dopo 30 minuti: rilanciare
  `tools/fleet build <cassa>`.

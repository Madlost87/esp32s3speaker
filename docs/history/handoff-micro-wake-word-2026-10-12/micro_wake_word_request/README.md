# Micro Wake Word Handoff Package

Questo pacchetto contiene le informazioni da inviare a chi deve produrre una wake word custom per il satellite vocale Galileo.

## Contenuto

- `REQUEST_TO_COLLEAGUE.md`: testo pronto da inoltrare.
- `DEVELOPER_QUICK_TRAINING_GUIDE.md`: guida rapida per chi deve trainare il modello.
- `FLASH_IDENTICAL_BOARD.md`: istruzioni per compilare/flashare una board uguale.
- `DEVICE_AUDIO_TARGET.md`: dettagli tecnici del device target.
- `SOFTWARE_VERSIONS.md`: versioni firmware/librerie e dettagli runtime rilevanti.
- `model_template/custom_wake_word.json`: template del manifest ESPHome microWakeWord v2.
- `example_model/`: esempio reale gia' funzionante nel firmware, basato su `hey_jarvis`.
- `example_full_flash_yaml/`: YAML completo di riferimento per una board identica.

## Output richiesto

Chiedere al collega di consegnare una coppia di file:

- `nome_wake_word.json`
- `nome_wake_word.tflite`

Il file JSON deve essere un manifest ESPHome microWakeWord v2 e deve puntare al relativo file `.tflite`.

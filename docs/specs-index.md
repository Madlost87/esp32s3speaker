# Indice delle spec — firmware e integrazioni Galileo

Questo indice è il punto di ripresa del lavoro. Distingue ciò che è concluso,
ciò che può iniziare subito e ciò che è intenzionalmente rinviato.

## Stato del programma

| Stato | Documento | Scopo | Prossima azione |
|---|---|---|---|
| Completata | [Spec 018 Core](../../../homeassistant/.openspec/specs/018-core-modularity-and-maintainability.md) | modularità Galileo Core | nessuna; conservare test e confini |
| Pronta, da iniziare | [Spec 011 firmware](spec-011-firmware-modularity-and-transport-hardening.md) | modularizzare il firmware senza cambiare `GLA1` | chiudere il gate di ingresso |
| Proposta futura | [Spec 017 discovery](../../../homeassistant/.openspec/specs/017-satellite-wifi-discovery-and-secure-provisioning.md) | discovery Wi-Fi, pairing e registry dinamico | attendere firmware/Core stabili |
| Da scrivere dopo 011-A | Spec `GLA2` Core + firmware | HMAC, anti-replay, rotazione chiavi e migrazione dual-stack | non iniziare prima della fase A |

## Ordine obbligatorio

```text
0. Gate di ingresso Spec 011
1. Spec 011, Fase A: refactor firmware compatibile
2. Pilot Garage + rollback + osservazione
3. Estensione individuale a Sala e Taverna
4. Spec GLA2 coordinata Core/firmware
5. Spec 017: discovery e provisioning sicuro
```

La numerazione non implica urgenza: lo stato e l'ordine sopra sono l'autorità.

## Regole di ripresa

- prima di una modifica leggere la Spec 011 e verificare il gate di ingresso;
- una sola cassa candidata per finestra di deploy;
- nessun deploy Core, firmware e dipendenze esterne nella stessa finestra;
- ogni passaggio deve produrre test eseguibili o un report sanitizzato;
- se emerge una nuova decisione di protocollo o sicurezza, aggiungere una spec
  prima di implementarla.

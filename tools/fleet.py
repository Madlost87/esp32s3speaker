#!/usr/bin/env python3
"""Gestione della flotta di satelliti Galileo (casse ESP32-S3).

Comandi:
  status                 stato live di ogni cassa (release, build, VoIP, wake word)
  build    [id ...]      compila e archivia i binari della release corrente
  rollout  [id ...]      OTA in ordine: canarino, pausa per il test, poi le altre
  rollback id [--to R]   reinstalla la build precedente (o la release R)
  release  VERSIONE      imposta la release nella base firmware
  new      id ...        crea il file di una cassa nuova e la registra
  docs                   rigenera la tabella "Build installate" di docs/satellites.md

Va lanciato con il Python del toolchain ESPHome (serve aioesphomeapi):
  /home/denny/esphome/.venv-2026.9.1/bin/python tools/fleet.py status
Guida completa: docs/fleet.md
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import hashlib
import json
import os
import re
import secrets as pysecrets
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
ESPHOME_DIR = REPO / "esphome"
ESPHOME_BIN = Path(os.environ.get("ESPHOME_BIN", Path(sys.executable).with_name("esphome")))
API_PORT = 6053
REBOOT_TIMEOUT_S = 240
COMPILE_TIMEOUT_S = 1800
DOCS_START = "<!-- fleet:installed:start -->"
DOCS_END = "<!-- fleet:installed:end -->"


# ---------------------------------------------------------------- config ----

class _Lenient(yaml.SafeLoader):
    """Reads ESPHome YAML without resolving !secret / !include / !lambda."""


_Lenient.add_multi_constructor(
    "!", lambda loader, tag, node: f"<{tag} {loader.construct_scalar(node)}>"
    if isinstance(node, yaml.ScalarNode) else None)


def load_yaml(path: Path) -> dict:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=_Lenient) or {}


class Fleet:
    def __init__(self, site: str):
        self.inventory_path = REPO / "fleet" / f"{site}.yaml"
        if not self.inventory_path.exists():
            sys.exit(f"Inventario mancante: {self.inventory_path}")
        self.inv = load_yaml(self.inventory_path)
        self.site = self.inv["site"]
        self.state_path = REPO / self.inv["state_file"]
        self.artifacts = Path(os.path.expanduser(self.inv["artifacts_dir"]))
        self.base = REPO / self.inv["firmware_base"]
        self.site_subs = load_yaml(REPO / self.inv["site_file"]).get("substitutions", {})

    # Devices -------------------------------------------------------------
    def devices(self, only: list[str] | None = None) -> list[dict]:
        out = []
        for d in self.inv["devices"]:
            cfg = REPO / d["config"]
            subs = dict(self.site_subs)
            subs.update(load_yaml(cfg).get("substitutions", {}))
            dev = {**d, "path": cfg, "subs": subs, "ip": str(subs["static_ip"]),
                   "name": subs["name"], "friendly_name": subs["friendly_name"]}
            dev["build_path"] = load_yaml(cfg).get("esphome", {}).get("build_path", f"build/{dev['name']}")
            out.append(dev)
        if only:
            known = {d["id"] for d in out}
            missing = set(only) - known
            if missing:
                sys.exit(f"Casse sconosciute: {', '.join(sorted(missing))} (note: {', '.join(sorted(known))})")
            out = [d for d in out if d["id"] in only]
        return out

    def release(self) -> str:
        m = re.search(r'^\s*firmware_release:\s*"([^"]+)"', self.base.read_text(encoding="utf-8"), re.M)
        if not m:
            sys.exit(f"firmware_release non trovato in {self.base}")
        return m.group(1)

    # State ---------------------------------------------------------------
    def state(self) -> dict:
        return json.loads(self.state_path.read_text(encoding="utf-8")) if self.state_path.exists() else {}

    def save_state(self, st: dict) -> None:
        self.state_path.write_text(json.dumps(st, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True).stdout.strip()


def now() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


# ------------------------------------------------------------------- API ----

async def probe(ip: str, timeout: float = 8.0) -> dict:
    """Device info plus the states used as health signals."""
    import aioesphomeapi

    client = aioesphomeapi.APIClient(ip, API_PORT, None)
    await asyncio.wait_for(client.connect(login=True), timeout)
    try:
        info = await client.device_info()
        entities, _ = await client.list_entities_services()
        by_key = {e.key: e.object_id for e in entities}
        states: dict[str, object] = {}
        client.subscribe_states(lambda s: states.__setitem__(by_key.get(s.key, "?"), getattr(s, "state", None)))
        await asyncio.sleep(2.5)
    finally:
        await client.disconnect()
    return {
        "name": info.name,
        "release": info.project_version or "-",
        "build_time": info.compilation_time,
        "esphome": info.esphome_version,
        "voip_state": states.get("voip_state"),
        "voip_endpoint": str(states.get("voip_endpoint") or ""),
        "wake_word": states.get("wake_word"),
        "uptime_s": states.get("uptime"),
    }


def health(dev: dict, p: dict, expect_release: str | None) -> list[str]:
    problems = []
    if p["name"] != dev["name"]:
        problems.append(f"nome {p['name']} invece di {dev['name']}")
    if expect_release and p["release"] != expect_release:
        problems.append(f"release {p['release']} invece di {expect_release}")
    if p["voip_state"] != "idle":
        problems.append(f"VoIP in stato {p['voip_state']}")
    if dev["ip"] not in p["voip_endpoint"]:
        problems.append("endpoint VoIP senza l'IP atteso")
    if p["wake_word"] is not True:
        problems.append("wake word spenta")
    return problems


async def wait_back(dev: dict, expect_release: str, deadline_s: int = REBOOT_TIMEOUT_S) -> tuple[dict | None, list[str]]:
    t0 = time.monotonic()
    last_err = "nessuna risposta"
    await asyncio.sleep(15)
    while time.monotonic() - t0 < deadline_s:
        try:
            p = await probe(dev["ip"])
            problems = health(dev, p, expect_release)
            # Right after boot VoIP and wake word may still be starting.
            if not problems or time.monotonic() - t0 > deadline_s - 30:
                return p, problems
            last_err = "; ".join(problems)
        except Exception as e:  # noqa: BLE001 - any API failure means "not back yet"
            last_err = type(e).__name__
        await asyncio.sleep(10)
    return None, [f"non tornata online in {deadline_s}s ({last_err})"]


# -------------------------------------------------------------- commands ----

def cmd_status(fleet: Fleet, args) -> int:
    rel = fleet.release()
    st = fleet.state()
    print(f"Sito {fleet.site} - release nel repository: {rel}\n")
    print(f"{'cassa':9} {'ip':15} {'release':15} {'build':20} {'VoIP':6} {'wake':5} {'acceso da':10} note")
    bad = 0

    async def one(dev):
        try:
            return dev, await probe(dev["ip"]), None
        except Exception as e:  # noqa: BLE001
            return dev, None, f"offline ({type(e).__name__})"

    async def run_all():
        return await asyncio.gather(*(one(d) for d in fleet.devices(args.devices)))

    for dev, p, err in asyncio.run(run_all()):
        if err:
            bad += 1
            print(f"{dev['id']:9} {dev['ip']:15} {'-':15} {'-':20} {'-':6} {'-':5} {'-':10} {err}")
            continue
        notes = health(dev, p, None)
        if p["release"] != rel:
            notes.append("da aggiornare" if p["release"] != "-" else "release non dichiarata (build precedente al sistema flotta)")
        rec = st.get(dev["id"], {})
        if rec and rec.get("release") not in (p["release"], None) and p["release"] != "-":
            notes.append(f"stato registrato {rec.get('release')}")
        if rec.get("build_time") and rec["build_time"][:16] != p["build_time"][:16]:
            notes.append("build diversa da quella registrata (prova in corso o OTA manuale)")
        up = p["uptime_s"]
        up_s = f"{int(up // 3600)}h{int(up % 3600 // 60):02d}m" if isinstance(up, (int, float)) else "-"
        bad += bool(health(dev, p, None))
        print(f"{dev['id']:9} {dev['ip']:15} {p['release']:15} {p['build_time'][:19]:20} {str(p['voip_state']):6} "
              f"{'on' if p['wake_word'] else 'off':5} {up_s:10} {'; '.join(notes)}")
    return 1 if bad else 0


def built_bin(dev: dict) -> Path:
    return ESPHOME_DIR / ".esphome" / dev["build_path"] / "build" / "firmware.ota.bin"


def cmd_build(fleet: Fleet, args) -> int:
    rel = fleet.release()
    dirty = bool(git("status", "--porcelain", "--", "esphome"))
    if dirty and not args.allow_dirty:
        sys.exit("esphome/ ha modifiche non committate: committare prima, oppure --allow-dirty per una build di prova.")
    commit = git("rev-parse", "--short", "HEAD") + ("-dirty" if dirty else "")
    outdir = fleet.artifacts / (rel if not dirty else f"{rel}-dev")
    outdir.mkdir(parents=True, exist_ok=True)
    manifest_path = outdir / "build.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    failed = []
    for dev in fleet.devices(args.devices):
        print(f"== {dev['id']}: compilo {dev['path'].name} (release {rel}, commit {commit})", flush=True)
        log = outdir / f"{dev['id']}.build.log"
        try:
            with log.open("w") as fh:
                rc = subprocess.run([str(ESPHOME_BIN), "compile", dev["path"].name], cwd=ESPHOME_DIR,
                                    stdout=fh, stderr=subprocess.STDOUT, timeout=COMPILE_TIMEOUT_S).returncode
        except subprocess.TimeoutExpired:
            rc = "timeout"
        text = log.read_text(errors="replace")
        m = re.search(r"config_hash=(0x[0-9a-f]+) build_time_str=(.+)", text)
        if rc != 0 or not m:
            print(f"   ERRORE ({rc}), log: {log}")
            failed.append(dev["id"])
            continue
        for kind in ("ota", "factory"):
            shutil.copy2(built_bin(dev).with_name(f"firmware.{kind}.bin"), outdir / f"{dev['id']}.{kind}.bin")
        art = outdir / f"{dev['id']}.ota.bin"
        manifest[dev["id"]] = {"release": rel, "commit": commit, "config_hash": m.group(1),
                               "build_time": m.group(2).strip(), "sha256_16": sha16(art), "built_at": now()}
        print(f"   ok  sha256 {manifest[dev['id']]['sha256_16']}  -> {art}")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    with (outdir / "SHA256SUMS").open("w") as fh:
        for b in sorted(outdir.glob("*.bin")):
            fh.write(f"{hashlib.sha256(b.read_bytes()).hexdigest()}  {b.name}\n")
    if failed:
        print(f"\nBuild fallite: {', '.join(failed)}")
    return 1 if failed else 0


def upload(dev: dict, binary: Path) -> bool:
    print(f"   OTA {binary.name} -> {dev['ip']}", flush=True)
    rc = subprocess.run([str(ESPHOME_BIN), "upload", dev["path"].name, "--device", dev["ip"], "--file", str(binary)],
                        cwd=ESPHOME_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if rc.returncode != 0:
        print("   upload fallito:\n" + "\n".join(rc.stderr.splitlines()[-5:]))
    return rc.returncode == 0


def record(fleet: Fleet, dev_id: str, entry: dict) -> None:
    st = fleet.state()
    prev = st.get(dev_id)
    if prev:
        hist = prev.pop("history", [])
        hist.insert(0, {k: prev[k] for k in ("release", "sha256_16", "artifact") if k in prev})
        entry["history"] = hist[:5]
    st[dev_id] = entry
    fleet.save_state(st)


def install(fleet: Fleet, dev: dict, binary: Path, release: str, meta: dict, rollback_bin: Path | None) -> bool:
    if not upload(dev, binary):
        return False
    p, problems = asyncio.run(wait_back(dev, release if not release.startswith("pre-") else None))
    if not problems:
        record(fleet, dev["id"], {"release": release, "firmware": meta.get("commit", "-"),
                                  "build_time": meta.get("build_time", p["build_time"] if p else "-"),
                                  "installed_at": now(), "sha256_16": sha16(binary), "artifact": str(binary)})
        print(f"   ok: {dev['id']} su {release}, VoIP {p['voip_state']}, wake word on")
        return True
    print(f"   CONTROLLO FALLITO su {dev['id']}: {'; '.join(problems)}")
    if rollback_bin and rollback_bin.exists():
        print(f"   rollback automatico a {rollback_bin}")
        if upload(dev, rollback_bin):
            asyncio.run(wait_back(dev, None))
    return False


def cmd_rollout(fleet: Fleet, args) -> int:
    rel = fleet.release()
    outdir = fleet.artifacts / rel
    manifest_path = outdir / "build.json"
    if not manifest_path.exists():
        sys.exit(f"Nessuna build per la release {rel}: lanciare prima `fleet.py build`.")
    manifest = json.loads(manifest_path.read_text())
    st = fleet.state()
    devs = fleet.devices(args.devices)
    devs.sort(key=lambda d: not d.get("canary"))
    for dev in devs:
        art = outdir / f"{dev['id']}.ota.bin"
        meta = manifest.get(dev["id"])
        if not meta or not art.exists() or sha16(art) != meta["sha256_16"]:
            sys.exit(f"Artefatto mancante o alterato per {dev['id']} in {outdir}")
    for i, dev in enumerate(devs):
        rec = st.get(dev["id"], {})
        if rec.get("release") == rel and rec.get("sha256_16") == manifest[dev["id"]]["sha256_16"] and not args.force:
            print(f"== {dev['id']}: gia' su {rel}, salto")
            continue
        print(f"== {dev['id']} ({dev['friendly_name']}){' [canarino]' if dev.get('canary') else ''}")
        prev = Path(rec["artifact"]) if rec.get("artifact") else None
        if not install(fleet, dev, outdir / f"{dev['id']}.ota.bin", rel, manifest[dev["id"]], prev):
            print("Rollout fermato. Le casse successive non sono state toccate.")
            return 1
        if dev.get("canary") and i < len(devs) - 1 and not args.yes:
            input(f"\nCanarino aggiornato. Prova {dev['friendly_name']} (wake word, 'che ore sono', "
                  "una chiamata), poi Invio per proseguire o Ctrl+C per fermarti. ")
    cmd_docs(fleet, args)
    return 0


def cmd_rollback(fleet: Fleet, args) -> int:
    dev = fleet.devices([args.device])[0]
    rec = fleet.state().get(dev["id"], {})
    if args.to:
        target = next((h for h in rec.get("history", []) if h.get("release") == args.to), None)
        art = fleet.artifacts / args.to / f"{dev['id']}.ota.bin"
        target = target or ({"release": args.to, "artifact": str(art)} if art.exists() else None)
    else:
        target = (rec.get("history") or [None])[0]
    if not target or not target.get("artifact") or not Path(target["artifact"]).exists():
        sys.exit(f"Nessuna build precedente disponibile per {dev['id']}.")
    binary = Path(target["artifact"])
    print(f"== rollback {dev['id']} a {target['release']} ({binary})")
    ok = install(fleet, dev, binary, target["release"], {"commit": "rollback"}, None)
    cmd_docs(fleet, args)
    return 0 if ok else 1


def cmd_release(fleet: Fleet, args) -> int:
    if not re.fullmatch(r"\d{4}\.\d{1,2}\.\d+", args.version):
        sys.exit("Formato release: AAAA.M.N, per esempio 2026.11.2")
    text = fleet.base.read_text(encoding="utf-8")
    new = re.sub(r'^(\s*firmware_release:\s*)"[^"]+"', rf'\g<1>"{args.version}"', text, count=1, flags=re.M)
    fleet.base.write_text(new, encoding="utf-8")
    print(f"Release impostata a {args.version} in {fleet.base.relative_to(REPO)}.\nPoi:\n"
          f"  git commit -am 'Release firmware {args.version}' && git tag fw-{args.version}\n"
          f"  tools/fleet.py build && tools/fleet.py rollout")
    return 0


DEVICE_TEMPLATE = """\
# {friendly} (area {area}). Solo identita': il comportamento e' nella
# base comune, rete e gruppi in {site_file}. Vedi docs/fleet.md.
substitutions:
  name: {name}
  friendly_name: {friendly}
  static_ip: {ip}
  voip_extension: "{ext}"
  direct_audio_port: "{audio}"
  direct_audio_control_port: "{control}"
  direct_audio_session_id: !secret {secret}

packages:
  site: !include {site_file}
  firmware: !include {base}

esphome:
  build_path: build/{name}
"""


def cmd_new(fleet: Fleet, args) -> int:
    devs = fleet.devices()
    if any(d["id"] == args.id for d in devs):
        sys.exit(f"La cassa {args.id} esiste gia'.")
    if any(d["ip"] == args.ip for d in devs):
        sys.exit(f"L'IP {args.ip} e' gia' usato.")
    name = args.name or f"satellite-{args.id}"
    friendly = args.friendly or f"Satellite {args.id.capitalize()}"
    ext = str(max(int(d["subs"]["voip_extension"]) for d in devs) + 1)
    audio = max(int(d["subs"]["direct_audio_port"]) for d in devs) + 2
    secret_key = f"galileo_audio_bridge_session_id_{args.id}"
    cfg = ESPHOME_DIR / f"{name}.yaml"
    if cfg.exists():
        sys.exit(f"{cfg} esiste gia'.")

    site_file = Path(fleet.inv["site_file"]).relative_to("esphome")
    cfg.write_text(DEVICE_TEMPLATE.format(
        friendly=friendly, area=args.area, name=name, ip=args.ip, ext=ext, audio=audio, control=audio + 1,
        secret=secret_key, site_file=site_file, base=fleet.base.name), encoding="utf-8")

    secrets_path = ESPHOME_DIR / "secrets.yaml"
    existing = secrets_path.read_text(encoding="utf-8") if secrets_path.exists() else ""
    if f"{secret_key}:" not in existing:
        with secrets_path.open("a", encoding="utf-8") as fh:
            fh.write(f"\n# Canale audio diretto autenticato per {friendly}.\n"
                     f'{secret_key}: "{pysecrets.token_hex(8)}"\n')

    with fleet.inventory_path.open("a", encoding="utf-8") as fh:
        fh.write(f"  - id: {args.id}\n    config: esphome/{cfg.name}\n    area: {args.area}\n")

    groups = {g.strip() for g in (fleet.site_subs.get("voip_ring_groups", "") + ","
                                  + fleet.site_subs.get("voip_conference_groups", "")).split(",") if g.strip()}
    if args.phonebook:
        pb_path = (REPO / fleet.inv["phonebook"]).resolve()
        pb = json.loads(pb_path.read_text(encoding="utf-8"))
        pb["extensions"].append({
            "extension": ext, "name": friendly, "kind": "esp32s3_esphome_voip_stack", "host": args.ip,
            "status": "active", "ring_group": fleet.site_subs.get("voip_ring_groups"),
            "conference_group": fleet.site_subs.get("voip_conference_groups"),
            "description": f"Satellite ESP32-S3 in {args.area}."})
        for g in pb["groups"]:
            if g["name"] in groups and friendly not in g["members"]:
                g["members"].append(friendly)
        pb_path.write_text(json.dumps(pb, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Rubrica aggiornata: {pb_path}")

    core_entry = {"id": f"satellite_{args.id}", "source": f"satellite_{args.id}",
                  "session_id": f"<valore di {secret_key} in esphome/secrets.yaml>",
                  "audio_port": audio, "control_port": audio + 1, "host": args.ip, "source_ip": args.ip}
    print(f"""
Creata {friendly}: {cfg.relative_to(REPO)}
  nome ESPHome {name}, IP {args.ip}, interno {ext}, UDP {audio}/{audio + 1}, area {args.area}
  segreto di sessione aggiunto a esphome/secrets.yaml ({secret_key})

Passi rimanenti (docs/fleet.md, "Aggiungere una cassa"):
  1. Router: riservare {args.ip} al MAC della scheda.
  2. Primo flash via USB:  cd esphome && esphome run {cfg.name} --device /dev/ttyACM0
  3. Galileo Core: aggiungere a GALILEO_DIRECT_VOICE_SATELLITES_JSON nel .env sul Raspberry
     {json.dumps(core_entry, ensure_ascii=False)}
     e riavviare galileo-core.
  4. Home Assistant: adottare il dispositivo ESPHome, assegnarlo all'area {args.area},
     aggiungerlo alle dashboard Casa / Voce / Sistema.{'' if args.phonebook else '''
  5. Rubrica: rilanciare con --phonebook oppure aggiornare voip/phonebook.json a mano.'''}
  6. Committare i due repository e verificare con `tools/fleet.py status`.""")
    return 0


def cmd_docs(fleet: Fleet, args) -> int:
    doc = REPO / "docs" / "satellites.md"
    text = doc.read_text(encoding="utf-8")
    if DOCS_START not in text:
        print(f"Marcatori {DOCS_START} assenti in {doc}: tabella non aggiornata.")
        return 1
    st = fleet.state()
    rows = ["| Cassa | Release | Firmware | Build (`build_time`) | Installata | SHA-256 OTA (16) |",
            "| --- | --- | --- | --- | --- | --- |"]
    for dev in fleet.devices():
        r = st.get(dev["id"], {})
        rows.append(f"| {dev['friendly_name']} | {r.get('release', '-')} | {r.get('firmware', '-')} | "
                    f"{r.get('build_time', '-')} | {r.get('installed_at', '-')} | `{r.get('sha256_16', '-')}` |")
    block = f"{DOCS_START}\n<!-- Generata da tools/fleet.py dal file {fleet.state_path.relative_to(REPO)}: non modificare a mano. -->\n" \
            + "\n".join(rows) + f"\n{DOCS_END}"
    text = re.sub(re.escape(DOCS_START) + r".*?" + re.escape(DOCS_END), lambda _: block, text, flags=re.S)
    doc.write_text(text, encoding="utf-8")
    print(f"Aggiornata la tabella in {doc.relative_to(REPO)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default="casa", help="inventario fleet/<sito>.yaml (default: casa)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("status"); p.add_argument("devices", nargs="*")
    p = sub.add_parser("build"); p.add_argument("devices", nargs="*")
    p.add_argument("--allow-dirty", action="store_true", help="build di prova con modifiche non committate")
    p = sub.add_parser("rollout"); p.add_argument("devices", nargs="*")
    p.add_argument("--yes", action="store_true", help="non fermarsi dopo il canarino")
    p.add_argument("--force", action="store_true", help="reinstalla anche se gia' aggiornata")
    p = sub.add_parser("rollback"); p.add_argument("device"); p.add_argument("--to", help="release da reinstallare")
    p = sub.add_parser("release"); p.add_argument("version")
    p = sub.add_parser("new"); p.add_argument("id", help="identificativo breve, es. cucina")
    p.add_argument("--ip", required=True); p.add_argument("--area", required=True)
    p.add_argument("--friendly", help="nome visibile (default: Satellite <Id>)")
    p.add_argument("--name", help="nome ESPHome (default: satellite-<id>)")
    p.add_argument("--phonebook", action="store_true", help="aggiorna anche la rubrica nel repo Home Assistant")
    sub.add_parser("docs")
    args = ap.parse_args()
    fleet = Fleet(args.site)
    return {"status": cmd_status, "build": cmd_build, "rollout": cmd_rollout, "rollback": cmd_rollback,
            "release": cmd_release, "new": cmd_new, "docs": cmd_docs}[args.cmd](fleet, args)


if __name__ == "__main__":
    sys.exit(main())

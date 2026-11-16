#!/usr/bin/env python3
"""Estime l'empreinte environnementale d'une session Claude Code (méthodologie EcoLogits).

Lit les transcripts JSONL de Claude Code (~/.claude/projects/<projet>/<session>.jsonl
et les sous-agents <session>/subagents/*.jsonl), compte les tokens réellement facturés
par requête et applique les formules d'EcoLogits (fourchette min/max).

Usage :
  python empreinte.py                       # session la plus récente du dossier courant
  python empreinte.py --session <id|chemin>  # une session précise
  python empreinte.py --since 2026-11-01     # toutes les sessions du projet depuis une date
  python empreinte.py --all-projects --since 2026-11-01
  python empreinte.py --json                 # sortie JSON (pour un rapport HTML)
Bibliothèque standard uniquement.
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "ecologits_data.json"), encoding="utf-8"))
C = DATA["constants"]
PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")


def lp(path):
    """Chemin long Windows (> 260 caractères) : préfixe d'accès étendu."""
    prefix = "\\\\?\\"
    path = os.path.abspath(path)
    if os.name == "nt" and not path.startswith(prefix):
        return prefix + path
    return path


def ls(directory, suffix=".jsonl"):
    try:
        return [os.path.join(directory, n) for n in os.listdir(lp(directory)) if n.endswith(suffix)]
    except OSError:
        return []


def all_transcripts():
    out = []
    for d in os.listdir(PROJECTS) if os.path.isdir(PROJECTS) else []:
        out += ls(os.path.join(PROJECTS, d))
    return out


def mtime(path):
    return os.path.getmtime(lp(path))


# ---------------------------------------------------------------- transcripts
def project_dir_for(cwd):
    name = re.sub(r"[^A-Za-z0-9]", "-", cwd)
    path = os.path.join(PROJECTS, name)
    return path if os.path.isdir(lp(path)) else None


def session_files(main_jsonl):
    sid = os.path.splitext(os.path.basename(main_jsonl))[0]
    subs = ls(os.path.join(os.path.dirname(main_jsonl), sid, "subagents"))
    return [main_jsonl] + sorted(subs)


def pick_sessions(args):
    if args.session:
        if os.path.isfile(args.session):
            return [args.session]
        hits = [f for f in all_transcripts() if os.path.basename(f) == args.session + ".jsonl"]
        if not hits:
            sys.exit(f"Session introuvable : {args.session}")
        return hits[:1]
    if args.all_projects:
        cands = all_transcripts()
    else:
        pdir = project_dir_for(os.path.abspath(args.cwd))
        if not pdir:
            cands = all_transcripts()
            print("(dossier projet non trouvé : on prend la session la plus récente toutes "
                  "provenances confondues)", file=sys.stderr)
            args.since = None
            return sorted(cands, key=mtime)[-1:]
        cands = ls(pdir)
    if not cands:
        sys.exit("Aucun transcript Claude Code trouvé.")
    if args.since:
        t0 = dt.datetime.fromisoformat(args.since).timestamp()
        return [f for f in cands if mtime(f) >= t0]
    return sorted(cands, key=mtime)[-1:]


def read_requests(files, since=None):
    """Une entrée par requête API (dédupliquée par message.id)."""
    reqs = {}
    for f in files:
        is_sub = os.sep + "subagents" + os.sep in f or "/subagents/" in f
        with open(lp(f), encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"usage"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = rec.get("message") or {}
                u = msg.get("usage")
                model = msg.get("model", "")
                if rec.get("type") != "assistant" or not u or model.startswith("<"):
                    continue
                if since and rec.get("timestamp", "") < since:
                    continue
                key = msg.get("id") or rec.get("uuid")
                det = u.get("output_tokens_details") or {}
                cur = {
                    "model": model,
                    "subagent": is_sub,
                    "out": u.get("output_tokens", 0) or 0,
                    "thinking": det.get("thinking_tokens", 0) or 0,
                    "in": u.get("input_tokens", 0) or 0,
                    "cache_read": u.get("cache_read_input_tokens", 0) or 0,
                    "cache_write": u.get("cache_creation_input_tokens", 0) or 0,
                }
                prev = reqs.get(key)
                if not prev or cur["out"] >= prev["out"]:
                    reqs[key] = cur
    return list(reqs.values())


# ---------------------------------------------------------------- EcoLogits
def resolve_model(name):
    models = DATA["models"]
    base = re.sub(r"-\d{8}$", "", name)  # retire un suffixe de date
    base = re.sub(r"\[.*\]$", "", base)   # ex. [1m]
    if base in models:
        return base, None
    for fam, fb in DATA["family_fallback"].items():
        if fam in base:
            return fb, f"{name} absent de la base EcoLogits : approximé par {fb}"
    return DATA["family_fallback"]["sonnet"], f"{name} inconnu : approximé par Sonnet"


def gpu_count(total_b):
    mem = C["memory_overhead"] * total_b * C["quantization_bits"] / 8
    n = math.ceil(mem / C["gpu_memory_gb"])
    return 2 ** math.ceil(math.log2(n))


def impacts(m, out_tokens, bound):
    """Impacts d'une requête pour la borne 'min' ou 'max' (unités SI usuelles)."""
    active = m["active_" + bound]
    total = m.get("total", active)
    gpus = gpu_count(total)
    pue = DATA["provider_anthropic"]["pue"][bound]
    wue = DATA["provider_anthropic"]["wue_onsite_l_per_kwh"][bound]
    mix = DATA["electricity_mixes"][DATA["provider_anthropic"]["datacenter_location"]]
    B = C["batch_size"]

    e_tok_kwh = (C["gpu_energy_alpha_wh"] * math.exp(C["gpu_energy_beta"] * B) * active
                 + C["gpu_energy_gamma_wh"]) / 1000
    latency = m["ttft"] + out_tokens / m["tps"]
    server_kwh = latency / 3600 * C["server_power_kw"] * gpus / C["server_gpus"] / B
    it_kwh = server_kwh + gpus * out_tokens * e_tok_kwh
    energy_kwh = pue * it_kwh

    share = latency / (C["hardware_lifespan_s"] * B)
    se, ge, k = C["server_embodied"], C["gpu_embodied"], gpus / C["server_gpus"]
    emb_gwp = share * (k * se["gwp_kgco2eq"] + gpus * ge["gwp_kgco2eq"])
    emb_adpe = share * (k * se["adpe_kgsbeq"] + gpus * ge["adpe_kgsbeq"])
    emb_pe = share * (k * se["pe_mj"] + gpus * ge["pe_mj"])
    return {
        "energy_wh": energy_kwh * 1000,
        "gwp_usage_g": energy_kwh * mix["gwp_kg_per_kwh"] * 1000,
        "gwp_embodied_g": emb_gwp * 1000,
        "adpe_mgsb": (energy_kwh * mix["adpe_kgsbeq_per_kwh"] + emb_adpe) * 1e6,
        "pe_kj": (energy_kwh * mix["pe_mj_per_kwh"] + emb_pe) * 1000,
        "water_l": it_kwh * (wue + pue * mix["wue_l_per_kwh"]),
    }


def add(acc, d):
    for k, v in d.items():
        acc[k] = acc.get(k, 0) + v


# ---------------------------------------------------------------- rapport
def compute(reqs):
    warnings, per_model = set(), {}
    tot = {"min": {}, "max": {}}
    tokens = {"out": 0, "thinking": 0, "in": 0, "cache_read": 0, "cache_write": 0,
              "requests": 0, "subagent_requests": 0, "subagent_out": 0}
    for r in reqs:
        key, w = resolve_model(r["model"])
        if w:
            warnings.add(w)
        m = DATA["models"][key]
        pm = per_model.setdefault(r["model"], {"requests": 0, "out": 0, "thinking": 0,
                                               "min": {}, "max": {}})
        pm["requests"] += 1
        pm["out"] += r["out"]
        pm["thinking"] += r["thinking"]
        for b in ("min", "max"):
            i = impacts(m, r["out"], b)
            i["gwp_g"] = i["gwp_usage_g"] + i["gwp_embodied_g"]
            add(tot[b], i)
            add(pm[b], i)
        for k in ("out", "thinking", "in", "cache_read", "cache_write"):
            tokens[k] += r[k]
        tokens["requests"] += 1
        if r["subagent"]:
            tokens["subagent_requests"] += 1
            tokens["subagent_out"] += r["out"]

    cc = DATA["context_estimate_wh_per_mtok"]
    context_wh = (tokens["in"] * cc["input"] + tokens["out"] * cc["output"]
                  + tokens["cache_read"] * cc["cache_read"]
                  + tokens["cache_write"] * cc["cache_write"]) / 1e6

    eq = DATA["equivalences"]
    mid = lambda k: (tot["min"].get(k, 0) + tot["max"].get(k, 0)) / 2
    equivalences = {
        "km_voiture_thermique": mid("gwp_g") / eq["voiture_thermique_g_per_km"]["value"],
        "km_tgv": mid("gwp_g") / eq["tgv_g_per_km"]["value"],
        "recharges_smartphone": mid("energy_wh") / eq["recharge_smartphone_wh"]["value"],
        "heures_ampoule_led": mid("energy_wh") / eq["ampoule_led_w"]["value"],
        "prompts_gemini_medians": mid("energy_wh") / eq["gemini_prompt_median_wh"]["value"],
        "verres_eau_25cl": mid("water_l") / 0.25,
    }
    return {
        "methodology": "EcoLogits v0.11.3 (sortie uniquement) - fourchette min/max",
        "tokens": tokens,
        "impacts": tot,
        "per_model": per_model,
        "context_estimate_wh": context_wh,
        "equivalences": equivalences,
        "warnings": sorted(warnings),
    }


def fmt(x, unit=""):
    if x == 0:
        return "0" + unit
    if abs(x) >= 100:
        s = f"{x:,.0f}".replace(",", " ")
    elif abs(x) >= 1:
        s = f"{x:.1f}"
    else:
        s = f"{x:.2g}"
    return s.replace(".", ",") + unit


def rng(res, key, unit):
    return f"{fmt(res['impacts']['min'].get(key, 0))} – {fmt(res['impacts']['max'].get(key, 0))}{unit}"


def text_report(res, label):
    t, e = res["tokens"], res["equivalences"]
    if not t["requests"]:
        return f"Aucune requête trouvée ({label})."
    lines = [
        f"## Empreinte estimée – {label}",
        "",
        f"Requêtes API : {t['requests']} (dont {t['subagent_requests']} par des sous-agents)",
        f"Tokens générés : {fmt(t['out'])} (dont {fmt(t['thinking'])} de réflexion, "
        f"{fmt(t['subagent_out'])} par des sous-agents)",
        f"Tokens lus en contexte : {fmt(t['in'] + t['cache_read'] + t['cache_write'])} "
        f"(dont {fmt(t['cache_read'])} relus depuis le cache)",
        "",
        "| Indicateur | Fourchette EcoLogits |",
        "|---|---|",
        f"| Énergie | {rng(res, 'energy_wh', ' Wh')} |",
        f"| Climat (GES) | {rng(res, 'gwp_g', ' g CO2e')} |",
        f"|  dont fabrication du matériel | {rng(res, 'gwp_embodied_g', ' g CO2e')} |",
        f"| Eau consommée | {rng(res, 'water_l', ' L')} |",
        f"| Ressources abiotiques (métaux) | {rng(res, 'adpe_mgsb', ' mg Sb éq.')} |",
        f"| Énergie primaire | {rng(res, 'pe_kj', ' kJ')} |",
        "",
        "Par modèle :",
    ]
    for name, pm in sorted(res["per_model"].items(), key=lambda kv: -kv[1]["max"]["energy_wh"]):
        lines.append(f"- {name} : {pm['requests']} req., {fmt(pm['out'])} tokens générés, "
                     f"{fmt(pm['min']['energy_wh'])} – {fmt(pm['max']['energy_wh'])} Wh")
    lines += [
        "",
        "Équivalences (valeur médiane de la fourchette) :",
        f"- {fmt(e['km_voiture_thermique'])} km en voiture thermique, ou {fmt(e['km_tgv'])} km en TGV",
        f"- {fmt(e['recharges_smartphone'])} recharges de smartphone, "
        f"{fmt(e['heures_ampoule_led'])} h d'ampoule LED 10 W",
        f"- {fmt(e['prompts_gemini_medians'])} requêtes Gemini « médianes » (0,24 Wh, Google 2025)",
        f"- {fmt(e['verres_eau_25cl'])} verres d'eau de 25 cl",
        "",
        f"Estimation complémentaire incluant la lecture du contexte (hors EcoLogits, "
        f"coefficients Couch 2026) : ~{fmt(res['context_estimate_wh'])} Wh",
    ]
    for w in res["warnings"]:
        lines.append(f"Avertissement : {w}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="identifiant ou chemin d'un transcript .jsonl")
    ap.add_argument("--cwd", default=os.getcwd(), help="dossier du projet (défaut : courant)")
    ap.add_argument("--since", help="date ISO (AAAA-MM-JJ) : toutes les sessions depuis cette date")
    ap.add_argument("--all-projects", action="store_true", help="tous les projets (avec --since)")
    ap.add_argument("--json", action="store_true", help="sortie JSON")
    args = ap.parse_args()

    mains = pick_sessions(args)
    if not mains:
        sys.exit("Aucune session trouvée pour ce périmètre.")
    files = [f for m in mains for f in session_files(m)]
    reqs = read_requests(files, since=args.since)
    res = compute(reqs)
    if args.since:
        label = f"sessions depuis le {args.since} ({len(mains)} session(s))"
    else:
        label = f"session {os.path.splitext(os.path.basename(mains[0]))[0][:8]}"
    res["scope"] = {"label": label, "sessions": len(mains), "files": len(files)}
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(text_report(res, label))


if __name__ == "__main__":
    main()

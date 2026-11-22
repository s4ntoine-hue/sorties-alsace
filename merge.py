#!/usr/bin/env python3
"""Fusionne les fichiers sources/*.json en un seul events.json pour l'application.

Usage : python3 merge.py [--today AAAA-MM-JJ]

Chaque fichier source contient {"source", "nom", "lu_le", "pages", "events": [...]}.
Règles :
- un événement terminé avant aujourd'hui est écarté ;
- deux événements sont des doublons s'ils ont la même commune (ou une commune inconnue),
  des titres proches et des dates qui se recouvrent ; ils sont fusionnés et gardent la
  liste de toutes leurs sources ;
- chaque événement reçoit un thème, un indicateur "gratuit" et un identifiant stable.
"""
import argparse, datetime, glob, hashlib, json, os, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))

STOP = set("le la les de des du d l un une et a au aux en sur pour par avec dans the of 2026 2027 festival exposition expo concert visite guidee".split())

THEMES = [
    ("Marchés de Noël & fêtes", r"noel|nicolas|rois mages|fete|bière|biere|kermesse|marche de noel|festivites"),
    ("Brocantes & marchés", r"brocante|braderie|puces|bourse|marche"),
    ("Concerts & festivals", r"concert|festival|jazz|son/lumi|musique|party"),
    ("Spectacles & cinéma", r"theatre|spectacle|cinema|film|danse|opera|humour|cirque"),
    ("Expos & salons", r"expo|salon|musee|art week|st-art"),
    ("Vin & gastronomie", r"degustation|vin|vigner|oenolog|cuisine|gastronom|repas|choco|brasserie|bredele"),
    ("Famille & enfants", r"famille|enfant|bebe|junior|jouet|lego|retrogaming|jeu|animation"),
    ("Sport & nature", r"sport|cross|course|foulees|nature|pedestre|balade|poney|randonn"),
    ("Visites & patrimoine", r"visite|memoire|patrimoine|histoire|conference|rencontre"),
    ("Ateliers", r"atelier|stage|artisanat|scrapbooking|cours"),
]


def norm(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9/ ]+", " ", s).strip()


def tokens(title):
    return {t for t in norm(title).split() if t not in STOP and len(t) > 1}


def same_commune(a, b):
    if not a or not b:
        return True
    return norm(a).replace(" ", "")[:10] == norm(b).replace(" ", "")[:10]


def overlap(a, b):
    a1, a2 = a["date_debut"], a.get("date_fin") or a["date_debut"]
    b1, b2 = b["date_debut"], b.get("date_fin") or b["date_debut"]
    if not a1 or not b1:
        return True
    return a1 <= b2 and b1 <= a2


def similar(a, b):
    ta, tb = tokens(a["titre"]), tokens(b["titre"])
    if not ta or not tb:
        return False
    inter = len(ta & tb)
    return inter / len(ta | tb) >= 0.5 or inter / min(len(ta), len(tb)) >= 0.8


def theme(e):
    text = norm(f'{e.get("categorie") or ""} {e["titre"]}')
    for name, rx in THEMES:
        if re.search(rx, text):
            return name
    return "Culture & vie locale"


def is_free(prix):
    return bool(prix) and norm(prix).startswith("gratuit")


def load_tr():
    try:
        return json.load(open(os.path.join(HERE, "traductions.json"), encoding="utf-8"))
    except FileNotFoundError:
        return {"titres": {}, "mots": {}}


def merge(today):
    sources, merged = [], []
    tr = load_tr()
    for path in sorted(glob.glob(os.path.join(HERE, "sources", "*.json"))):
        src = json.load(open(path, encoding="utf-8"))
        sources.append({k: src.get(k) for k in ("source", "nom", "lu_le", "pages", "note", "pays")} | {"nb": len(src["events"])})
        for raw in src["events"]:
            e = dict(raw)
            fr = tr["titres"].get(e["titre"])
            if fr and fr != e["titre"]:
                e["titre_original"], e["titre"] = e["titre"], fr
            if e.get("categorie"):
                for a, b in tr["mots"].items():
                    e["categorie"] = e["categorie"].replace(a, b)
            end = e.get("date_fin") or e.get("date_debut")
            if end and end < today:
                continue
            url = e.pop("url", None)
            if not url:  # pas de lien par événement : renvoyer vers la page lue
                m = re.search(r"https?://\S+", " ".join(src.get("pages") or []))
                url = m.group(0) if m else None
            ref = {"source": src["source"], "nom": src["nom"], "url": url}
            dup = next((m for m in merged if same_commune(m["commune"], e["commune"]) and overlap(m, e) and similar(m, e)), None)
            if dup:
                if ref["source"] not in {s["source"] for s in dup["sources"]}:
                    dup["sources"].append(ref)
                for k in ("horaires", "lieu", "prix", "commune", "date_fin"):
                    if not dup.get(k) and e.get(k):
                        dup[k] = e[k]
                if e.get("date_debut") and dup["date_debut"] and e["date_debut"] < dup["date_debut"]:
                    dup["date_debut"] = e["date_debut"]
                continue
            e["sources"] = [ref]
            e["pays"] = raw.get("pays") or src.get("pays") or "FR"
            merged.append(e)
    for e in merged:
        e["theme"] = theme(e)
        e["gratuit"] = is_free(e.get("prix"))
        e["id"] = hashlib.sha1(f'{norm(e.get("titre_original") or e["titre"])}|{norm(e["commune"])}|{e["date_debut"]}'.encode()).hexdigest()[:10]
    merged.sort(key=lambda e: (e["date_debut"] or "9999", e["titre"]))
    return {"genere_le": today, "sources": sources, "events": merged}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default=datetime.date.today().isoformat())
    args = ap.parse_args()
    out = merge(args.today)
    json.dump(out, open(os.path.join(HERE, "events.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    multi = sum(len(e["sources"]) > 1 for e in out["events"])
    print(f'{len(out["events"])} événements, dont {multi} trouvés sur plusieurs sources')
    for s in out["sources"]:
        print(f'  {s["nom"]}: {s["nb"]} lus')

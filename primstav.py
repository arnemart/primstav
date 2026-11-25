#!/usr/bin/env python3
"""Poster dagens merkedag fra primstaven til Mastodon."""

import argparse
import datetime
import json
import os
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

MERKEDAGER = Path(__file__).with_name("merkedager.json")
MÅNEDER = ["januar", "februar", "mars", "april", "mai", "juni", "juli",
           "august", "september", "oktober", "november", "desember"]


def finn_merkedag(dato):
    nøkkel = dato.strftime("%m-%d")
    for dag in json.loads(MERKEDAGER.read_text()):
        if dag["dato"] == nøkkel:
            return dag
    return None


def lag_tekst(dag, dato):
    navn, *andre_navn = dag["navn"]
    detaljer = []
    if andre_navn:
        detaljer.append("Også kalt: " + ", ".join(andre_navn))
    if dag.get("merknad"):
        detaljer.append(dag["merknad"])
    if dag["merker"]:
        detaljer.append("Merke på primstaven: " + ", ".join(dag["merker"]))
    avsnitt = [
        f"I dag, {dato.day}. {MÅNEDER[dato.month - 1]}, er det {navn}.",
        dag.get("snu"),
        "\n".join(detaljer),
        dag["wikipedia"],
    ]
    return "\n\n".join(a for a in avsnitt if a)


def post(tekst, dato):
    url = os.environ.get("MASTODON_URL", "https://snabel.party").rstrip("/")
    token = os.environ["MASTODON_TOKEN"]
    data = json.dumps({
        "status": tekst,
        "visibility": os.environ.get("MASTODON_VISIBILITY", "public"),
        "language": "no",
    }).encode()
    req = urllib.request.Request(
        f"{url}/api/v1/statuses",
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            # Hindrer dobbeltposting hvis jobben kjøres flere ganger samme dag
            "Idempotency-Key": f"primstav-{dato.isoformat()}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)["url"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="skriv ut i stedet for å poste")
    parser.add_argument("--dato", type=datetime.date.fromisoformat,
                        help="bruk denne datoen (ÅÅÅÅ-MM-DD) i stedet for i dag")
    args = parser.parse_args()

    dato = args.dato or datetime.datetime.now(ZoneInfo("Europe/Oslo")).date()
    dag = finn_merkedag(dato)
    if dag is None:
        print(f"{dato}: ingen merkedag")
        return

    tekst = lag_tekst(dag, dato)
    if args.dry_run:
        print(tekst)
        return
    print(f"{dato}: postet {post(tekst, dato)}")


if __name__ == "__main__":
    sys.exit(main())

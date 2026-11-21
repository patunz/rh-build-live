#!/bin/sh
# Salva in data/ lo stato attuale del build, letto dall'indirizzo scritto in live.json.
# La pagina usa questa copia quando il pod non risponde o quando live.json ha "base": null.
set -eu
cd "$(dirname "$0")"
U=$(python3 -c "import json; print(json.load(open('live.json'))['base'] or '')")
: "${U:?live.json non ha un indirizzo}"
for f in sys.json now.json; do curl -fsS -m 60 -o "data/$f.tmp" "$U/$f"; done
curl -fsS -m 300 -o data/events.bin.tmp "$U/events?from=0"
for f in sys.json now.json events.bin; do mv "data/$f.tmp" "data/$f"; done
cat data/sys.json; echo

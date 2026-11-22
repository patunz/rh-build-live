# Rebuilding Alpöge's RH Lean archive, live

A live view of an independent, from-scratch `lake build` of the Lean archive
with which Levent Alpöge announced a proof of the Riemann Hypothesis
(175,187 files; original material at <https://alpo.ge/>).

**This page claims nothing about the correctness of the proof.** It shows a
build in progress. The checks that matter come after the build, and their
outcomes will be added here as they close:

1. the build reaching `Main` with no errors;
2. the axioms the final theorems depend on (A. Sutherland's `Audit.lean`);
3. a comparison of the resulting `.olean` files with A. Sutherland's manifest
   (partial so far, complete once the build ends).

A re-check with `lean4checker` is not decided yet.

The page is in English and Italian (button at the bottom right, or `?lang=it` / `?lang=en`).

## What you are looking at

Each stroke is one file: it starts when Lean begins compiling it and ends when
it is done. The horizontal axis is time, the vertical axis is the dependency
level, and the threads link a file to the files it imports. The colours are the
top-level folders of the archive. Click a stroke to see what it rests on; use
the slider to go back in time.

## How it works

- `index.html` and the import graph (`meta.json`, `level.u8`, `lib.u8`,
  `depoff.u32`, `deps.u32`, `names.txt`) are static files in this repository.
- `live.json` holds the address of the build machine. While the build runs,
  the page reads three things from it: finished files (`/events`), files being
  compiled (`/now.json`) and machine status (`/sys.json`); `/file` (theorem
  statements of one file, rate-limited) is currently switched off. The server is
  `pod/srv_pub.py`: read-only, nothing else.
- `data/` is the last saved snapshot (`istantanea.sh` refreshes it). The page
  falls back to it when the machine does not answer, and will keep working as
  a replay after the build.
- `risultati.json` is the list of checks shown in the "Controlli" tab.
- `architettura.html` is a second page, linked from the first: one column per
  theory on the axis of dependency levels, ribbons for the imports between
  theories, the hypothesis structures and the final chain. Its data
  (`arch.json`, `blk.u16`) hold names of files and declarations, not statements
  or proofs. It is generated from our private version by
  `strumenti/architettura_pubblica.py`.
- `comunita.json` holds our own texts for the "Community" panel: the threads
  of work, our contributions and the list of projects. Issue and PR titles,
  states and counts are read live from GitHub's public API in the visitor's
  browser (cached for ten minutes); the grouping into threads is our reading
  of the titles.
- `aggiornamenti.json` is the log shown in the same panel. A scheduled
  workflow (`.github/workflows/aggiornamenti.yml`) runs
  `strumenti/aggiornamenti.py` twice a day and appends one entry with what
  GitHub reports for the interval: issues and PRs opened, merged and closed,
  stars, the state of our own issues and of our build. Facts only; the page
  composes the sentences.

## What is not here

The archive's sources and compiled files are not redistributed: the archive
declares no licence. This repository holds only module names and the import
graph derived from them. The page can also quote the *statements* of the
theorems in a file, attributed to Levent Alpöge and never the proofs; this is
switched off (`"enunciati"` in `live.json`, and on the server): we have asked
the author's permission and are waiting for his answer.

## Who

Lucio Patone, working with Claude (Anthropic) as an assistant.

---

# La ricostruzione dell'archivio Lean di Alpöge, dal vivo

Una vista in diretta di un `lake build` indipendente, da zero, dell'archivio
Lean con cui Levent Alpöge ha annunciato una dimostrazione dell'ipotesi di
Riemann (175.187 file; materiale originale su <https://alpo.ge/>).

**Questa pagina non afferma nulla sulla correttezza della dimostrazione.**
Mostra un build in corso. I controlli che contano vengono dopo, e i loro esiti
saranno aggiunti qui man mano che si chiudono: il build fino a `Main` senza
errori, gli assiomi usati dai teoremi finali, il confronto degli `.olean` con
il manifest di A. Sutherland (per ora parziale).

I sorgenti e i file compilati dell'archivio non sono ridistribuiti, perché
l'archivio non dichiara una licenza: nel repository ci sono solo i nomi dei
moduli e il grafo degli import che se ne ricava. La pagina può anche citare i
soli enunciati dei teoremi di un file, attribuiti a Levent Alpöge e mai le
dimostrazioni; la funzione è spenta: abbiamo chiesto il permesso all'autore e aspettiamo la
sua risposta.

Lucio Patone, con Claude (Anthropic) come assistente.

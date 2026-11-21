"""Versione pubblica della pagina dell'architettura. Si può rilanciare su una versione più nuova del file privato.
Uso: architettura.py <architettura.html privata> <arch.json privato> <cartella del repo pubblico>"""
import json, sys

src, arch, out = sys.argv[1:4]
t = open(src, encoding='utf-8').read()


def sub(old, new, count=1):
    global t
    assert t.count(old) == count, (t.count(old), old[:70])
    t = t.replace(old, new)


# --- testi: un build in corso, non una verifica conclusa
sub('<title>Architettura della dimostrazione</title>', '<title>Archivio RH di Alpöge: l\'architettura</title>')
sub('<div class="eyebrow">Verifica formale dell\'ipotesi di Riemann</div>', '<div class="eyebrow">Architettura dell\'archivio Lean di Alpöge</div>')
sub('La parte piena è già verificata.', 'La parte piena è già compilata nel nostro build.')
sub("' file, ' + nf(dn) + ' verificati.'", "' file, ' + nf(dn) + ' compilati.'")
sub("['Verificati', nf(dn)", "['Compilati', nf(dn)")
sub("Verificati finora ' + nf(nDone)", "Compilati finora ' + nf(nDone)")

# --- la traccia dell'autore resta fuori finché Lucio non decide: bottone nascosto, dati tolti da arch.json
sub('<button type="button" class="ic" id="bTrace" aria-pressed="false">', '<button type="button" class="ic" id="bTrace" aria-pressed="false" hidden>')
if '[hidden]' not in t:
    sub('</style>', '[hidden]{display:none!important}\n</style>')

# --- dati in diretta: dalla macchina del build scritta in live.json, oppure dall'istantanea in data/
sub("// ---- dati\nasync function pollEvents() {\n  const buf = await (await fetch('events?from=' + nEv)).arrayBuffer(),",
    "// ---- dati: gli statici stanno accanto alla pagina; eventi ed enunciati arrivano dalla macchina del build (live.json),\n"
    "// e per gli eventi c'è l'istantanea in data/ quando la macchina non risponde\n"
    "let base = null;\n"
    "async function pollEvents() {\n"
    "  const r = await (base != null ? fetch(base + '/events?from=' + nEv, { signal: AbortSignal.timeout(30000) }) : fetch('data/events.bin'));\n"
    "  if (!r.ok) throw new Error('events');\n"
    "  const buf = await r.arrayBuffer(),")
sub("  const ev = () => pollEvents().catch(() => { $('status').textContent = 'Il pod non risponde: riprovo.'; });\n  await ev(); setInterval(ev, 30000);",
    "  try { base = (await (await fetch('live.json?' + Date.now())).json()).base || null; } catch (e) { base = null; }\n"
    "  if (base != null) { try { await pollEvents(); } catch (e) { base = null; } }\n"
    "  if (base != null) setInterval(() => pollEvents().catch(() => {}), 30000);\n"
    "  else await pollEvents().catch(() => { $('status').textContent = 'I dati del build non sono raggiungibili: la figura mostra solo la struttura.'; });")

# --- enunciati: solo dal vivo, con il limite di richieste e l'attribuzione
sub("function openFile(i, name, copie, focus) {",
    "const getFile = (i) => (base == null ? Promise.resolve({ error: 'off' }) : fetch(base + '/file?i=' + i, { signal: AbortSignal.timeout(20000) }).then((r) => (r.ok ? r.json() : { error: r.status })));\n"
    "function openFile(i, name, copie, focus) {")
sub("fetch('file?i=' + i).then((r) => r.json()).then((d) => { if (file && file.i === i) { info = d; decl = ",
    "getFile(i).then((d) => { if (file && file.i === i) { info = d; if (d.error) { renderPanel(); return; } decl = ")
sub("fetch('file?i=' + copie[0]).then((r) => r.json()).then(", "getFile(copie[0]).then(")
sub("if (info.error) { body.append(el('div', 'note', 'Il sorgente non è raggiungibile in questo momento. Riprova tra poco.')); return; }",
    "if (info.error) { body.append(el('div', 'note', info.error === 'off' ? 'Gli enunciati si leggono dalla macchina del build, che in questo momento non è collegata.' : info.error === 429 ? 'Troppe richieste in questo momento: riprova tra un minuto.' : 'L\\'enunciato non è raggiungibile in questo momento. Riprova tra poco.')); return; }")
sub("  diagram(body, d.s, accent);\n",
    "  diagram(body, d.s, accent);\n"
    "  if (info.fonte) { const n = el('div', 'note', 'Fonte: ' + info.fonte + '. Le dimostrazioni non sono riprodotte. '), a = el('a', '', 'Archivio originale'); a.href = 'https://alpo.ge/'; a.rel = 'noopener'; a.style.color = 'inherit'; n.append(a, '.'); body.append(n); }\n")
open(out + '/architettura.html', 'w', encoding='utf-8').write(t)

d = json.load(open(arch, encoding='utf-8'))
d['passi'] = []
json.dump(d, open(out + '/arch.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
left = [l[:140] for l in t.split('\n') if 'erific' in l]
print('ok', len(t), 'resta "verific":', left)

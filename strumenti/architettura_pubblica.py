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
sub('aria-label="Architettura della dimostrazione:', 'aria-label="Architettura dell\'archivio:')
sub('<title>Architettura della dimostrazione</title>', '<title>Archivio RH di Alpöge: l\'architettura</title>')
sub('<div class="eyebrow">Verifica formale dell\'ipotesi di Riemann</div>', '<div class="eyebrow">Architettura dell\'archivio Lean di Alpöge</div>')
sub('La parte piena è già verificata.', 'La parte piena è già compilata nel nostro build.')
sub("' file, ' + nf(dn) + ' verificati.'", "' file, ' + nf(dn) + ' compilati.'")
sub("['Verificati', nf(dn)", "['Compilati', nf(dn)")
sub("Verificati finora ' + nf(nDone)", "Compilati finora ' + nf(nDone)")

# --- la mappa fotografa l'archivio originale: il repository della comunità nel frattempo viene riscritto
sub('Fai clic su una colonna per aprirla.</div>', 'Fai clic su una colonna per aprirla. La mappa descrive l\'archivio pubblicato il 20 novembre 2026 (commit 40e56bab): il repository della comunità nel frattempo viene riscritto e non coincide più con questa fotografia.</div>')

# --- la traccia dell'autore resta fuori finché Lucio non decide: bottone nascosto, dati tolti da arch.json
sub('<button type="button" class="ic" id="bTrace" aria-pressed="false">', '<button type="button" class="ic" id="bTrace" aria-pressed="false" hidden>')
if '[hidden]' not in t:
    sub('</style>', '[hidden]{display:none!important}\n</style>')

# --- dati in diretta: dalla macchina del build scritta in live.json, oppure dall'istantanea in data/
sub("// ---- dati\nasync function pollEvents() {\n  const buf = await (await fetch('events?from=' + nEv)).arrayBuffer(),",
    "// ---- dati: gli statici stanno accanto alla pagina; eventi ed enunciati arrivano dalla macchina del build (live.json),\n"
    "// e per gli eventi c'è l'istantanea in data/ quando la macchina non risponde\n"
    "let base = null, stmtOn = false;\n"
    "async function pollEvents() {\n"
    "  const r = await (base != null ? fetch(base + '/events?from=' + nEv, { signal: AbortSignal.timeout(30000) }) : fetch('data/events.bin'));\n"
    "  if (!r.ok) throw new Error('events');\n"
    "  const buf = await r.arrayBuffer(),")
sub("  const ev = () => pollEvents().catch(() => { $('status').textContent = 'Il pod non risponde: riprovo.'; });\n  await ev(); setInterval(ev, 30000);",
    "  try { const lj = await (await fetch('live.json?' + Date.now())).json(); base = lj.base || null; stmtOn = lj.enunciati === true; } catch (e) { base = null; }\n"
    "  if (base != null) { try { await pollEvents(); } catch (e) { base = null; } }\n"
    "  if (base != null) setInterval(() => pollEvents().catch(() => {}), 30000);\n"
    "  else await pollEvents().catch(() => { $('status').textContent = 'I dati del build non sono raggiungibili: la figura mostra solo la struttura.'; });")

# --- enunciati: solo dal vivo, con il limite di richieste e l'attribuzione
sub("function openFile(i, name, copie, focus) {",
    "const getFile = (i) => (!stmtOn ? Promise.resolve({ error: 'spenti' }) : base == null ? Promise.resolve({ error: 'off' }) : fetch(base + '/file?i=' + i, { signal: AbortSignal.timeout(20000) }).then((r) => (r.ok ? r.json() : { error: r.status })));\n"
    "function openFile(i, name, copie, focus) {")
sub("fetch('file?i=' + i).then((r) => r.json()).then((d) => { if (file && file.i === i) { info = d; decl = ",
    "getFile(i).then((d) => { if (file && file.i === i) { info = d; if (d.error) { renderPanel(); return; } decl = ")
sub("fetch('file?i=' + copie[0]).then((r) => r.json()).then(", "getFile(copie[0]).then(")
sub("if (info.error) { body.append(el('div', 'note', 'Il sorgente non è raggiungibile in questo momento. Riprova tra poco.')); return; }",
    "if (info.error) { body.append(el('div', 'note', info.error === 'spenti' ? 'Gli enunciati dei teoremi non sono mostrati. L\\'archivio è di Levent Alpöge ed è pubblicato senza licenza: gli abbiamo chiesto il permesso di citarli qui, con attribuzione, e aspettiamo la sua risposta. L\\'archivio si scarica da alpo.ge.' : info.error === 'off' ? 'Gli enunciati si leggono dalla macchina del build, che in questo momento non è collegata.' : info.error === 429 ? 'Troppe richieste in questo momento: riprova tra un minuto.' : 'L\\'enunciato non è raggiungibile in questo momento. Riprova tra poco.')); return; }")
sub("  diagram(body, d.s, accent);\n",
    "  diagram(body, d.s, accent);\n"
    "  if (info.fonte) { const n = el('div', 'note', 'Fonte: ' + info.fonte + '. Le dimostrazioni non sono riprodotte. '), a = el('a', '', 'Archivio originale'); a.href = 'https://alpo.ge/'; a.rel = 'noopener'; a.style.color = 'inherit'; n.append(a, '.'); body.append(n); }\n")

# --- due lingue, come nel tracciato: ogni scritta italiana diventa T(italiano, inglese)
import re
sub("piena la parte verificata", "piena la parte compilata")
PAIRS = r"""
' blocchi minori' | ' minor blocks'
'livello di dipendenza' | 'dependency level'
'Struttura di ipotesi al livello ' | 'Hypothesis structure at level '
'. Campi: ' | '. Fields: '
'non letti' | 'not read'
' file. Al livello ' | ' files. At level '
' file, ' | ' files, '
' compilati.' | ' compiled.'
'Teorema' | 'Theorem'
'Definizione' | 'Definition'
'Abbreviazione' | 'Abbreviation'
'Struttura' | 'Structure'
'Classe' | 'Class'
'Tipo induttivo' | 'Inductive type'
'Istanza' | 'Instance'
'Chiudi la scheda' | 'Close the panel'
'Dal PDF, non dai sorgenti' | 'From the PDF, not from the sources'
'Traccia dell\'autore' | 'The author\'s outline'
'I sottoblocchi troppo piccoli per avere una colonna propria' | 'Sub-blocks too small to have a column of their own'
' file · liv. ' | ' files · lev. '
'Torna a ' | 'Back to '
'Gruppo di file che si importano tra loro; il nome sono le parole che li distinguono' | 'A group of files that import one another; the name is the words that set them apart'
'File della teoria che non formano un blocco riconoscibile' | 'Files of the theory that do not form a recognisable block'
'Spazio dei nomi ' | 'Namespace '
'Blocco' | 'Block'
'Snodi e vertici' | 'Hubs and peaks'
'Ipotesi' | 'Hypotheses'
'File' | 'Files'
'Compilati' | 'Compiled'
'Dichiarazioni' | 'Declarations'
'Livelli' | 'Levels'
'da ' | 'from '
' a ' | ' to '
', mediana ' | ', median '
'Strutture di ipotesi' | 'Hypothesis structures'
'Nomi che ricorrono nelle dichiarazioni' | 'Names that recur in the declarations'
'Numero di file in cui la parola compare nel nome del file o di una dichiarazione. Sono nomi, non un riassunto di cosa fa il blocco.' | 'Number of files where the word appears in the name of the file or of a declaration. These are names, not a summary of what the block does.'
' import' | ' imports'
'Poggia su' | 'Rests on'
'Lo usano' | 'Used by'
' sotto · ' | ' below · '
' sopra' | ' above'
' sotto' | ' below'
'liv. ' | 'lev. '
' · liv. ' | ' · lev. '
'Snodi tra i teoremi' | 'Hubs among the theorems'
'Snodi' | 'Hubs'
'Teoremi che poggiano su molte dichiarazioni e sono usati da molte: raccolgono tanto lavoro e lo passano avanti. Sono i primi posti dove guardare.' | 'Theorems that rest on many declarations and are used by many: they gather a lot of work and pass it on. They are the first places to look.'
'Hanno molto sotto e molto sopra insieme: raccolgono tanto lavoro e lo passano a molti. Sono i primi posti dove guardare.' | 'They have a lot below and a lot above at once: they gather a lot of work and pass it on to many. They are the first places to look.'
'Vertici' | 'Peaks'
'I file più alti del blocco: dove il suo lavoro culmina.' | 'The highest files of the block: where its work culminates.'
'Fondamenta' | 'Foundations'
'I più usati dal resto del progetto. Di solito lemmi di base.' | 'The most used by the rest of the project. Usually basic lemmas.'
'Per gli snodi, "sotto" e "sopra" contano le dichiarazioni raggiunte seguendo le citazioni lette nel testo delle dimostrazioni: una lettura testuale, precisa al 98% circa ma incompleta, perché tattiche automatiche e notazione col punto usano lemmi senza nominarli. ' | 'For hubs, "below" and "above" count the declarations reached by following the citations read in the text of the proofs: a textual reading, about 98% precise but incomplete, because automatic tactics and dot notation use lemmas without naming them. '
'Per vertici e fondamenta contano i file, seguendo gli import, e sono esatti. Uno snodo è centrale nel grafo: è un indizio su dove guardare, non la prova che sia centrale nell\'idea.' | 'For peaks and foundations they count files, following the imports, and are exact. A hub is central in the graph: it is a hint about where to look, not proof that it is central to the idea.'
'Nessuna struttura di ipotesi in questo blocco.' | 'No hypothesis structures in this block.'
'Strutture che raccolgono come ipotesi risultati presi dalla letteratura. Non sono assiomi: il teorema finale non ha ipotesi, quindi da qualche parte vengono soddisfatte. Dove, non l\'abbiamo ancora tracciato per tutte.' | 'Structures that collect, as hypotheses, results taken from the literature. They are not axioms: the final theorem has no hypotheses, so somewhere they are discharged. Where, we have not yet traced for all of them.'
'Leggo il sorgente dal pod.' | 'Reading from the build machine.'
'Gli enunciati dei teoremi non sono mostrati. L\'archivio è di Levent Alpöge ed è pubblicato senza licenza: gli abbiamo chiesto il permesso di citarli qui, con attribuzione, e aspettiamo la sua risposta. L\'archivio si scarica da alpo.ge.' | 'Theorem statements are not shown. The archive is by Levent Alpöge and was published without a licence: we have asked his permission to quote them here, with attribution, and are waiting for his answer. The archive can be downloaded from alpo.ge.'
'Gli enunciati si leggono dalla macchina del build, che in questo momento non è collegata.' | 'Statements are read from the build machine, which is not connected right now.'
'Troppe richieste in questo momento: riprova tra un minuto.' | 'Too many requests right now: try again in a minute.'
'L\'enunciato non è raggiungibile in questo momento. Riprova tra poco.' | 'The statement cannot be reached right now. Try again shortly.'
'Righe' | 'Lines'
'Teoremi e lemmi' | 'Theorems and lemmas'
'Definizioni' | 'Definitions'
'Enunciato per esteso' | 'Statement in full'
'Viene da una delle ' | 'It comes from one of the '
' copie di enunciato: file che riscrivono un risultato in forma leggibile e lo chiudono richiamando questo.' | ' statement copies: files that restate a result in readable form and close it by invoking this one.'
'Questo file non contiene dichiarazioni.' | 'This file contains no declarations.'
'Dichiarazioni del file' | 'Declarations in the file'
'Enunciato precedente' | 'Previous statement'
'Enunciato successivo' | 'Next statement'
' di ' | ' of '
'. Le dimostrazioni non sono riprodotte. ' | '. Proofs are not reproduced. '
'Archivio originale' | 'Original archive'
'Il grafo delle citazioni non è caricato sul pod.' | 'The citation graph is not loaded on the build machine.'
' dichiarazioni' | ' declarations'
'La usano' | 'Used by'
'E altre ' | 'And more: '
'Cita direttamente' | 'Cites directly'
'Citato da' | 'Cited by'
'Citazioni lette nel testo della dimostrazione, non dall\'elaborazione di Lean: quelle mostrate sono quasi sempre vere, ma possono mancarne.' | 'Citations read in the text of the proof, not from Lean\'s elaboration: the ones shown are almost always true, but some may be missing.'
'struttura richiesta' | 'required structure'
'se vale' | 'if'
'per ogni' | 'for all'
'Tesi' | 'Conclusion'
'La tesi non si isola dal testo.' | 'The conclusion could not be isolated from the text.'
' file' | ' files'
'non localizzato' | 'not located'
' file · liv. medio ' | ' files · mean lev. '
' file di lavoro matematico in ' | ' files of mathematical work in '
' teorie. Fuori dalla figura ' | ' theories. Outside the figure '
' copie di enunciato. Compilati finora ' | ' statement copies. Compiled so far '
' file su ' | ' files out of '
'I dati dell\'architettura non sono raggiungibili. Ricarica la pagina per riprovare.' | 'The architecture data cannot be reached. Reload the page to try again.'
'I dati del build non sono raggiungibili: la figura mostra solo la struttura.' | 'The build data cannot be reached: the figure shows the structure only.'
"""
pairs = dict(l.split(' | ') for l in PAIRS.strip('\n').split('\n'))
a = t.index('<script>')
head, js = t[:a], t[a:]
rx = re.compile('|'.join(re.escape(k) for k in sorted(pairs, key=len, reverse=True)))
used = set()
def rep(m):
    used.add(m.group(0)); return 'T(' + m.group(0) + ', ' + pairs[m.group(0)] + ')'
js = rx.sub(rep, js)
print('non trovate:', [k for k in pairs if k not in used])
t = head + js
sub("'use strict';\n", """'use strict';
// lingua: ?lang= nell'indirizzo, poi la scelta salvata, poi quella del browser; italiano solo se chiesto
let EN = true;
{ let l = new URLSearchParams(location.search).get('lang'); if (!l) { try { l = localStorage.getItem('lang'); } catch (e) {} } EN = !/^it/i.test(l || navigator.language || 'en'); }
const T = (it, en) => (EN ? en : it);
document.documentElement.lang = EN ? 'en' : 'it';
// le etichette italiane dentro i dati, in inglese
const DATI = { 'Langlands locale': 'local Langlands', 'Siegel–Weil, formula di massa': 'Siegel–Weil, mass formula', 'altezze': 'heights', 'campi di funzioni, Frobenius': 'function fields, Frobenius', 'caratteri di Dirichlet': 'Dirichlet characters', 'caratteri di Hecke': 'Hecke characters', 'cristallino, Hodge p-adico': 'crystalline, p-adic Hodge', 'determinante': 'determinant', 'funzioni L': 'L-functions', 'gruppi unitari': 'unitary groups', 'letteratura, teoremi pubblicati': 'literature, published theorems', 'modularità, patching': 'modularity, patching', 'moltiplicazione complessa': 'complex multiplication', 'pendenze di Bost': 'Bost slopes', 'serie discrete': 'discrete series', 'somme di Gauss': 'Gauss sums', 'zeri, non annullamento': 'zeros, non-vanishing', 'EveryCharacter ⇒ ipotesi di Riemann': 'EveryCharacter ⇒ Riemann hypothesis', 'Ipotesi di letteratura': 'Literature hypotheses', 'letteratura + VWin ⇒ EveryCharacter': 'literature + VWin ⇒ EveryCharacter' };
const dato = (s) => DATI[s] || s.replace(/^Altre(?= ·|$)/, 'Others').replace(/ · altri$/, ' · others');
function translateData() {
  for (const x of A.teorie) x.nome = dato(x.nome);
  for (const s of A.subs) { s.nome = dato(s.nome); if (s.chiavi) for (const k of s.chiavi) k[0] = dato(k[0]); }
  for (const s of A.spina) s.etichetta = dato(s.etichetta);
}
""")
sub("toLocaleString('it-IT')", "toLocaleString(EN ? 'en-GB' : 'it-IT')")
sub("    A = a[0]; LV = A.livelli;", "    A = a[0]; if (EN) translateData(); LV = A.livelli;")
# scritte dell'HTML e bottone della lingua
sub('<a class="ic" href="./">Tracciato del build</a>', '<a class="ic" id="aBuild" href="./">Tracciato del build</a>\n<button type="button" class="ic" id="bLang"></button>')
sub('<div class="eyebrow">Architettura', '<div class="eyebrow" id="eyebrow">Architettura')
sub('<h1>Architettura</h1>', '<h1 id="h1">Architettura</h1>')
sub("requestAnimationFrame(draw);\nboot();", """document.title = T('Archivio RH di Alpöge: l\\'architettura', 'Alpöge RH archive: the architecture');
$('eyebrow').textContent = T('Architettura dell\\'archivio Lean di Alpöge', 'Architecture of Alpöge\\u2019s Lean archive');
$('h1').textContent = T('Architettura', 'Architecture');
$('lede').textContent = T($('lede').textContent, 'Each column is a theory: one bar per level, as long as the files it has at that height, on the same scale for all. Where there is no bar there are no files. The filled part is already compiled in our build. The ribbons are the imports from one theory to another. Click a column to open it. This map describes the archive published on 20 November 2026 (commit 40e56bab): the community repository is being rewritten in the meantime and no longer matches this snapshot.');
$('cv').setAttribute('aria-label', T($('cv').getAttribute('aria-label'), 'Architecture of the archive: one column per theory on the axis of dependency levels, as wide as the files it has at each level, with ribbons for the imports between theories'));
$('bUp').textContent = T('Tutte le teorie', 'All theories');
$('status').textContent = T('Caricamento dei dati', 'Loading data');
$('bTrace').textContent = T('Traccia dell\\'autore', 'The author\\u2019s outline');
$('bFlow').textContent = T('Nastri', 'Ribbons');
$('aBuild').textContent = T('Tracciato del build', 'Build trace');
$('bFull').title = T('Schermo intero', 'Full screen'); $('bFull').setAttribute('aria-label', $('bFull').title);
$('bLang').textContent = EN ? 'IT' : 'EN';
$('bLang').onclick = () => { const l = EN ? 'it' : 'en'; try { localStorage.setItem('lang', l); } catch (e) {} const u = new URL(location.href); u.searchParams.set('lang', l); location.href = u.href; };
requestAnimationFrame(draw);
boot();""")
open(out + '/architettura.html', 'w', encoding='utf-8').write(t)

d = json.load(open(arch, encoding='utf-8'))
d['passi'] = []
json.dump(d, open(out + '/arch.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
left = [l[:140] for l in t.split('\n') if 'erific' in l]
print('ok', len(t), 'resta "verific":', left)

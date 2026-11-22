#!/usr/bin/env python3
"""Aggiunge una voce al diario della scheda Comunità: solo fatti letti da GitHub, nessun testo scritto a mano.

Per ogni giro registra che cosa è successo nel repository del gruppo dall'ultima voce: issue aperte e chiuse,
PR aperte, unite e chiuse, come si distribuiscono tra i filoni di comunita.json, che cosa è cambiato sulle
nostre issue, stelle e fork, e a che punto è il nostro build. La pagina compone le frasi nelle due lingue.

Uso: aggiornamenti.py [cartella del repo]. In GitHub Actions legge GITHUB_TOKEN dall'ambiente."""
import datetime, json, os, re, sys, urllib.request

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, 'aggiornamenti.json')
MAX_VOCI, MAX_ELENCO, PRIMA_FINESTRA_ORE = 40, 8, 12


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'rh-build-live'})
    token = os.environ.get('GITHUB_TOKEN')
    if token and url.startswith('https://api.github.com/'):
        req.add_header('Authorization', 'Bearer ' + token)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def carica(nome, vuoto):
    try:
        return json.load(open(os.path.join(ROOT, nome), encoding='utf-8'))
    except FileNotFoundError:
        return vuoto


comm = carica('comunita.json', None)
stato = carica('aggiornamenti.json', {'voci': []})
repo = comm['repo']
ora = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
iso = lambda d: d.strftime('%Y-%m-%dT%H:%M:%SZ')
da = stato.get('fino') or iso(ora - datetime.timedelta(hours=PRIMA_FINESTRA_ORE))

# tutte le voci toccate dall'ultima volta, a pagine
voci = []
for pagina in range(1, 11):
    blocco = get('https://api.github.com/repos/%s/issues?state=all&sort=updated&direction=desc&per_page=100&since=%s&page=%d' % (repo, da, pagina))
    voci += blocco
    if len(blocco) < 100:
        break


def filone(v):
    """Indice del filone di comunita.json: prima per numero, poi per parole nel titolo; -1 se nessuno."""
    for k, f in enumerate(comm['filoni']):
        if v['number'] in f['numeri']:
            return k
    for k, f in enumerate(comm['filoni']):
        if f.get('parole') and re.search(f['parole'], v['title'], re.I):
            return k
    return -1


breve = lambda v: {'n': v['number'], 't': v['title'], 'u': v['user']['login'], 'url': v['html_url']}
dopo = lambda t: bool(t) and t > da
gruppi = {'issue_aperte': [], 'issue_chiuse': [], 'pr_aperte': [], 'pr_unite': [], 'pr_chiuse': []}
per_filone = [0] * (len(comm['filoni']) + 1)
for v in voci:
    pr = v.get('pull_request')
    if dopo(v['created_at']):
        gruppi['pr_aperte' if pr else 'issue_aperte'].append(v)
        per_filone[filone(v)] += 1
    if pr and dopo(pr.get('merged_at')):
        gruppi['pr_unite'].append(v)
    elif dopo(v.get('closed_at')):
        gruppi['pr_chiuse' if pr else 'issue_chiuse'].append(v)

voce = {'da': da, 'a': iso(ora)}
for nome, elenco in gruppi.items():
    elenco.sort(key=lambda v: v['number'])
    voce[nome] = {'n': len(elenco), 'elenco': [breve(v) for v in elenco[:MAX_ELENCO]]}
voce['per_filone'] = per_filone

# le nostre issue: stato e commenti, e che cosa è cambiato dall'ultima voce
prima = stato.get('nostre', {})
adesso, nostre = {}, []
for o in comm['nostri']:
    v = get('https://api.github.com/repos/%s/issues/%d' % (repo, o['numero']))
    k = str(o['numero'])
    adesso[k] = {'aperta': v['state'] == 'open', 'commenti': v['comments']}
    p = prima.get(k)
    if p is None or p != adesso[k]:
        nostre.append({'n': o['numero'], 't': v['title'], 'url': v['html_url'], 'aperta': adesso[k]['aperta'],
                       'commenti': v['comments'], 'commenti_prima': p['commenti'] if p else None,
                       'aperta_prima': p['aperta'] if p else None})
voce['nostre'] = nostre

r = get('https://api.github.com/repos/' + repo)
voce['stelle'], voce['fork'] = r['stargazers_count'], r['forks_count']
voce['stelle_prima'], voce['fork_prima'] = stato.get('stelle'), stato.get('fork')

# il nostro build, se la macchina risponde
try:
    base = carica('live.json', {}).get('base')
    if base:
        s = get(base + '/sys.json', timeout=15)
        voce['build'] = {'n': s['n'], 'tot': carica('meta.json', {}).get('n'), 'errori': s['err'], 'uscita': s['exit']}
except Exception:
    pass

mosso = any(voce[k]['n'] for k in gruppi) or nostre
nuovo = {'fino': iso(ora), 'stelle': voce['stelle'], 'fork': voce['fork'], 'nostre': adesso,
         'voci': ([voce] if mosso else []) + stato.get('voci', [])}
nuovo['voci'] = nuovo['voci'][:MAX_VOCI]
json.dump(nuovo, open(FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('da', da, 'a', iso(ora), {k: voce[k]['n'] for k in gruppi}, 'nostre cambiate:', len(nostre), 'voce scritta:', bool(mosso))

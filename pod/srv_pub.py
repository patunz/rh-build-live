# Server pubblico della dashboard: sola lettura.
# Uso: python3 srv_pub.py <origine consentita> [altre origini]
#
#   /events, /now.json, /sys.json   i tre dati in diretta del build
#   /file?i=N                       gli enunciati dei teoremi del file N, letti dal sorgente
#
# Non serve file statici e non accetta caricamenti. Dei sorgenti espone solo gli enunciati
# (dal nome del teorema fino al := escluso), mai le dimostrazioni: l'archivio è di Levent Alpöge
# ed è stato pubblicato senza licenza, quindi qui se ne cita lo stretto necessario, con un limite
# al numero di richieste perché non diventi un modo per scaricarlo in blocco.
import collections, http.server, json, re, sys, threading, time, urllib.parse

MON = '/root/mon/'
SRC = '/root/rh/lean/src/'
ORIGINS = set(sys.argv[1:])
FONTE = 'Levent Alpöge, https://alpo.ge/ (archivio pubblicato senza licenza; qui solo gli enunciati, a scopo di studio)'
PER_INDIRIZZO, IN_TUTTO, FINESTRA = 40, 240, 60.0   # richieste di /file al minuto
MAX_ENUNCIATI, MAX_CARATTERI = 60, 6000

MOD = r'(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|nonrec|public)\s+)*'
RT = re.compile(r'^[ \t]*' + MOD + r'(theorem|lemma)\s+(\S+)', re.M)
RD = re.compile(r'^[ \t]*' + MOD + r'(?:def|abbrev|structure|class|instance|inductive)\b', re.M)
_names = []
_viste = collections.defaultdict(collections.deque)
_lock = threading.Lock()


def names():
    if not _names:
        _names.extend(l.strip() for l in open(MON + 'names.txt'))
    return _names


def concesso(chi):
    """Limite di richieste: per indirizzo e in tutto, su una finestra di un minuto."""
    ora = time.time()
    with _lock:
        for k in (chi, '*'):
            d = _viste[k]
            while d and ora - d[0] > FINESTRA:
                d.popleft()
        if len(_viste[chi]) >= PER_INDIRIZZO or len(_viste['*']) >= IN_TUTTO:
            return False
        _viste[chi].append(ora)
        _viste['*'].append(ora)
        if len(_viste) > 5000:
            for k in [k for k, d in _viste.items() if not d]:
                del _viste[k]
        return True


def enunciato(text, start):
    """Dal nome del teorema fino al := (o where, o |) che sta fuori da ogni parentesi: la dimostrazione resta fuori."""
    seg = text[start:start + MAX_CARATTERI * 2]
    depth, cut = 0, len(seg)
    for i, ch in enumerate(seg):
        if ch in '([{⦃⟨':
            depth += 1
        elif ch in ')]}⦄⟩':
            depth -= 1
        elif depth <= 0 and (seg.startswith(':=', i) or seg.startswith('where', i)
                             or (ch == '\n' and seg[i + 1:].lstrip(' ').startswith('|'))):
            cut = i
            break
    s = ' '.join(seg[:cut].split())
    return s if len(s) <= MAX_CARATTERI else s[:MAX_CARATTERI - 1] + '…'


def file_info(i):
    name = names()[i]
    text = open(SRC + name.replace('.', '/') + '.lean', encoding='utf-8', errors='replace').read()
    decls = [{'k': m.group(1), 'n': m.group(2), 's': enunciato(text, m.end())} for m in RT.finditer(text)]
    return {'name': name, 'lines': text.count('\n') + 1, 'bytes': len(text.encode('utf-8')), 'defs': len(RD.findall(text)),
            'ndecl': len(decls), 'decls': decls[:MAX_ENUNCIATI], 'fonte': FONTE}


class H(http.server.BaseHTTPRequestHandler):
    def reply(self, body, ctype, code=200):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Vary', 'Origin')
        origin = self.headers.get('Origin')
        if origin in ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlsplit(self.path)
        q = urllib.parse.parse_qs(u.query)
        try:
            if u.path == '/events':
                k = max(0, int(q.get('from', ['0'])[0]))
                with open(MON + 'events.bin', 'rb') as f:
                    f.seek(k * 12)
                    body = f.read()
                return self.reply(body[:len(body) // 12 * 12], 'application/octet-stream')
            if u.path in ('/now.json', '/sys.json'):
                return self.reply(open(MON + u.path[1:], 'rb').read(), 'application/json')
            if u.path == '/file':
                chi = self.headers.get('CF-Connecting-IP') or self.client_address[0]
                if not concesso(chi):
                    return self.reply(b'{"errore": "troppe richieste, riprova tra un minuto"}', 'application/json', code=429)
                i = int(q['i'][0])
                if not 0 <= i < len(names()):
                    return self.reply(b'not found', 'text/plain', code=404)
                return self.reply(json.dumps(file_info(i), ensure_ascii=False).encode(), 'application/json')
        except (OSError, ValueError, KeyError, IndexError):
            return self.reply(b'not available', 'text/plain', code=503)
        self.reply(b'not found', 'text/plain', code=404)

    def log_message(self, *a):
        pass


http.server.ThreadingHTTPServer(('127.0.0.1', 8081), H).serve_forever()

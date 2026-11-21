# Server pubblico della dashboard: sola lettura, solo i tre dati in diretta.
# Uso: python3 srv_pub.py <origine consentita> [altre origini]
# Non serve file statici, non legge i sorgenti e non accetta caricamenti.
import http.server, sys, urllib.parse

MON = '/root/mon/'
ORIGINS = set(sys.argv[1:])


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
        try:
            if u.path == '/events':
                k = max(0, int(urllib.parse.parse_qs(u.query).get('from', ['0'])[0]))
                with open(MON + 'events.bin', 'rb') as f:
                    f.seek(k * 12)
                    body = f.read()
                return self.reply(body[:len(body) // 12 * 12], 'application/octet-stream')
            if u.path in ('/now.json', '/sys.json'):
                return self.reply(open(MON + u.path[1:], 'rb').read(), 'application/json')
        except (OSError, ValueError):
            return self.reply(b'not available', 'text/plain', code=503)
        self.reply(b'not found', 'text/plain', code=404)

    def log_message(self, *a):
        pass


http.server.ThreadingHTTPServer(('127.0.0.1', 8081), H).serve_forever()

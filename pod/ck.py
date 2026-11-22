# Osserva da fuori il controllore (leanchecker), che non stampa nulla mentre lavora.
# Ogni 5 secondi legge /proc/<pid>: tempo di calcolo, memoria, thread, e dalle mappature l'elenco dei .olean del
# progetto che il processo ha aperto. Ogni modulo visto per la prima volta diventa un record in ck.bin
# (u32 indice del file, f32 secondi dall'avvio del controllore); lo stato corrente va in ck.json.
# "Caricato" vuol dire aperto dal controllore, non ancora ricontrollato: da fuori non si vede di più.
import json, os, re, struct, subprocess, sys, time

MON = '/root/mon/'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/root/fin/checker_all.out'
LIB = '/root/rh/lean/.lake/build/lib/lean/'
RX = re.compile(re.escape(LIB) + r'(\S+)\.olean$', re.M)
TICK = os.sysconf('SC_CLK_TCK')
PAGE = os.sysconf('SC_PAGE_SIZE')

idx = {l.strip(): i for i, l in enumerate(open(MON + 'names.txt'))}
pids = subprocess.run(['pgrep', '-f', '^leanchecker '], capture_output=True, text=True).stdout.split()
if not pids:
    sys.exit('nessun controllore in esecuzione')
pid = pids[0]
stat = open('/proc/%s/stat' % pid).read().rsplit(')', 1)[1].split()
uptime = float(open('/proc/uptime').read().split()[0])
start = time.time() - (uptime - int(stat[19]) / TICK)   # istante di avvio del processo

seen = set()
if os.path.exists(MON + 'ck.bin') and '--riprendi' in sys.argv:
    d = open(MON + 'ck.bin', 'rb').read()
    seen = {struct.unpack_from('<I', d, k)[0] for k in range(0, len(d) - 7, 8)}
else:
    open(MON + 'ck.bin', 'wb').close()


def scrivi(stato):
    with open(MON + 'ck.json.tmp', 'w') as f:
        json.dump(stato, f)
    os.replace(MON + 'ck.json.tmp', MON + 'ck.json')


ultimo = {}
while True:
    try:
        st = open('/proc/%s/stat' % pid).read().rsplit(')', 1)[1].split()
        maps = open('/proc/%s/maps' % pid).read()
    except OSError:
        break
    t = time.time() - start
    nuovi = []
    for m in RX.finditer(maps):
        i = idx.get(m.group(1).replace('/', '.'))
        if i is not None and i not in seen:
            seen.add(i)
            nuovi.append(i)
    if nuovi:
        with open(MON + 'ck.bin', 'ab') as f:
            f.write(b''.join(struct.pack('<If', i, t) for i in nuovi))
    ultimo = {'avvio': start, 't': round(t, 1), 'cpu_utente': int(st[11]) / TICK, 'cpu_sistema': int(st[12]) / TICK,
              'thread': int(st[17]), 'ram_mb': int(st[21]) * PAGE >> 20, 'mappature': maps.count('\n'),
              'caricati': len(seen), 'uscita_byte': os.path.getsize(OUT), 'in_corso': True, 'esito': None}
    scrivi(ultimo)
    time.sleep(5)

# il processo è finito: l'esito lo scrive lo script che lo ha lanciato, in fondo al file d'uscita
time.sleep(3)
m = re.search(r'CHECKER_EXIT (\d+) (\S+)', open(OUT, errors='replace').read())
ultimo.update(in_corso=False, esito=int(m.group(1)) if m else None, fine=m.group(2) if m else None,
              uscita_byte=os.path.getsize(OUT))
scrivi(ultimo)

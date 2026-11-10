"""
doelen_over_tijd.py -- how Dutch WFD (KRW) goals for surface water bodies changed over time.

Run:  python -I analysis\doelen_over_tijd.py        (Python 3, standard library only; pandas NOT needed)

Inputs (relative to project root = parent of this folder):
  WKP_download_doelen_*/WKP_KRW-doelen_Nederland_<YEAR>_*.csv      YEAR 2013..2025
  WKP_download_OWL_*/WKP_KRW-oppervlaktewaterlichamen_Nederland_<YEAR>_*.csv   (VoorgangerCode, status, type)
  WKP_download_oordelen_*/WKP_KRW-toestandsoordelen-beknopt_Nederland_<YEAR>_*.csv (measured EKR; Q4)

Outputs (analysis/output/):
  doelen_ekr_long.csv          tidy goals (EKR elements + Ptot/Ntot) per distinct goal set
  doelen_changes_summary.csv   changes between pairs of goal sets, by element / status / beheerder
  report_tables.txt            all numbers used in docs/analysis/doelen_over_tijd.md (plain text)
  q4_link_table.csv            per water body x EKR element: old goal, new goal, measured EKR (Q4)

GOAL DEFINITION (verified in section 1 of the report):
  EKR elements (FYTOPL, MAFAUNA, OVWFLORA, VIS): lower bound of class 'goed' (>= value)  (higher = more ambitious)
  Ptot, Ntot, Cl:  upper bound of class 'goed' (<= value)                                  (lower  = more ambitious)
  ZICHT (Secchi depth, m): lower bound of class 'goed'                                      (higher = more ambitious)
  O2, pH, T, Nanorg: not analysed.
Goal sets: each file holds one set; consecutive years with identical content are merged into one set,
labelled by the FIRST file year in which it appears (e.g. '2015' = files 2015-2017).
Water body matching: WaterlichaamCode upper-cased; VoorgangerCode from OWL used where present.
"""
import csv, glob, os, re, math, random, hashlib, collections
from statistics import median

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'analysis', 'output')
os.makedirs(OUT, exist_ok=True)
EKR_EL = ['FYTOPL', 'MAFAUNA', 'OVWFLORA', 'VIS']
PN_EL = ['Ptot', 'Ntot']
ALL_EL = EKR_EL + PN_EL + ['Cl', 'ZICHT']
SIGN = {e: 1 for e in EKR_EL}
SIGN['ZICHT'] = 1
for e in PN_EL + ['Cl']:
    SIGN[e] = -1          # +1: higher goal = more ambitious
TOL = 1e-9
REPORT = []


def P(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    REPORT.append(s)


def table(header, rows):
    P('| ' + ' | '.join(map(str, header)) + ' |')
    P('|' + '---|' * len(header))
    for r in rows:
        P('| ' + ' | '.join(map(str, r)) + ' |')
    P('')


def fl(x):
    try:
        return float(str(x).replace(',', '.'))
    except Exception:
        return None


def q(v, p):
    v = sorted(v)
    if not v:
        return None
    k = (len(v) - 1) * p
    f = math.floor(k)
    c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def rnd(x, n=3):
    return None if x is None else round(x, n)


def ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    sa = sum((x - ma) ** 2 for x in a)
    sb = sum((y - mb) ** 2 for y in b)
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sa * sb)


def spearman(a, b):
    return pearson(ranks(a), ranks(b)) if len(a) > 2 else None


def spearman_ci(a, b, B=500, seed=1):
    rg = random.Random(seed)
    n = len(a)
    res = []
    if n < 10:
        return None
    for _ in range(B):
        idx = [rg.randrange(n) for _ in range(n)]
        r = spearman([a[i] for i in idx], [b[i] for i in idx])
        if r is not None:
            res.append(r)
    return (rnd(q(res, .025)), rnd(q(res, .975)))


# ---------------------------------------------------------------- load
def rd(path, cols=None):
    with open(path, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f, delimiter=';'):
            yield r if cols is None else {c: r[c] for c in cols}


def find(pattern):
    g = glob.glob(os.path.join(ROOT, pattern))
    return g[0] if g else None


YEARS = list(range(2013, 2026))
raw = {}
for y in YEARS:
    raw[y] = list(rd(find(f'WKP_download_doelen_*/WKP_KRW-doelen_Nederland_{y}_*.csv')))
P('## Loaded goal files')
table(['file year', 'rows', 'bodies (upper-case code)', 'description'],
      [(y, len(raw[y]), len({r['WaterlichaamCode'].upper() for r in raw[y]}), raw[y][0]['KRWdoelensetOmschrijving'][:90]) for y in YEARS])

cases = collections.defaultdict(set)
for y in YEARS:
    for r in raw[y]:
        cases[r['WaterlichaamCode'].upper()].add(r['WaterlichaamCode'])
ncase = sum(1 for v in cases.values() if len(v) > 1)
P(f'Codes whose original spelling differs between/within years (case): {ncase} of {len(cases)}')
P('Classificatie values over all files:', dict(collections.Counter(r['Classificatie'] for y in YEARS for r in raw[y])))
P('Eenheid by element over all files:', {e: dict(collections.Counter(r['Eenheid'] for y in YEARS for r in raw[y] if r['KRWkwaliteitselementCode'] == e)) for e in ALL_EL})
P('')


# ---------------------------------------------------------------- distinct goal sets
def signature(rows):
    """Identity of a goal set = goal content of the analysed elements (code, element, class, symbols, values).
    Metadata (names, status, watertype) and non-analysed elements (O2, pH, T) are ignored, because those were
    found to change between files (e.g. watertype codes, O2 bounds re-typed) without changing the analysed goals."""
    h = hashlib.sha1()
    for t in sorted((r['WaterlichaamCode'].upper(), r['KRWkwaliteitselementCode'],
                     r['Classificatie'], r['OndergrensSymbool'], r['OndergrensWaarde'], r['BovengrensSymbool'], r['BovengrensWaarde'])
                    for r in rows if r['KRWkwaliteitselementCode'] in ALL_EL):
        h.update('|'.join(t).encode() + b'\n')
    return h.hexdigest()


sets = []
for y in YEARS:
    sg = (raw[y][0]['KRWdoelensetOmschrijving'], signature(raw[y]))
    if sets and sets[-1]['sig'] == sg:
        sets[-1]['files'].append(y)
    else:
        sets.append(dict(label=str(y), files=[y], rows=raw[y], sig=sg, desc=sg[0]))
for s in sets:
    m = re.search(r'vastgesteld in (\d{4})', s['desc'])
    s['desc_year'] = m.group(1) if m else '?'
    s['filespan'] = f"{s['files'][0]}-{s['files'][-1]}" if len(s['files']) > 1 else str(s['files'][0])
P('## Distinct goal sets (identical content in consecutive years merged)')
table(['set label', 'files', 'description year', 'rows', 'description'], [(s['label'], s['filespan'], s['desc_year'], len(s['rows']), s['desc'][:100]) for s in sets])
SETBY = {s['label']: s for s in sets}

# ---------------------------------------------------------------- goal extraction + anomaly checks
ANOM = collections.defaultdict(collections.Counter)
ANOM_EX = collections.defaultdict(list)


CUR_EL = ['']


def anomaly(kind, lab, ex):
    kind = f"{kind} [{'EKR' if CUR_EL[0] in EKR_EL else CUR_EL[0]}]"
    ANOM[kind][lab] += 1
    if len(ANOM_EX[kind]) < 5:
        ANOM_EX[kind].append((lab,) + ex)


def build(s):
    lab = s['label']
    grp = collections.defaultdict(lambda: collections.defaultdict(list))
    meta = {}
    for r in s['rows']:
        el = r['KRWkwaliteitselementCode']
        cu = r['WaterlichaamCode'].upper()
        if cu not in meta:
            meta[cu] = dict(code=r['WaterlichaamCode'], naam=r['WaterlichaamNaam'], beheerder=r['WaterbeheerderNaam'],
                            status=r['WaterlichaamKRWstatus'], watertype=r['WaterlichaamKRWwatertypeCode'], provincie=r['ProvincieNaam'])
        if el in ALL_EL:
            grp[(cu, el)][r['Classificatie']].append(r)
    goals = {}
    for (cu, el), cl in grp.items():
        CUR_EL[0] = el
        for c, lst in cl.items():
            if len(lst) > 1:
                anomaly('duplicate class rows', lab, (cu, el, c))
        if 'goed' not in cl:
            anomaly("no 'goed' row", lab, (cu, el))
            continue
        g = cl['goed'][0]
        ol, ou = fl(g['OndergrensWaarde']), fl(g['BovengrensWaarde'])
        higher_better = el in EKR_EL or el == 'ZICHT'
        if higher_better:
            val = ol
            if g['OndergrensSymbool'] != '>=':
                anomaly("goed lower-bound symbol is not '>='", lab, (cu, el, g['OndergrensSymbool']))
        else:
            val = ou
            if g['BovengrensSymbool'] != '<=':
                anomaly("goed upper-bound symbol is not '<='", lab, (cu, el, g['BovengrensSymbool']))
        if val is None:
            anomaly('goal bound missing/non-numeric', lab, (cu, el))
            continue
        order = ['slecht', 'ontoereikend', 'matig', 'goed']
        if higher_better:
            lows = [(c, fl(cl[c][0]['OndergrensWaarde'])) for c in order if c in cl]
            lows = [(c, v) for c, v in lows if v is not None]
            if any(lows[i][1] > lows[i + 1][1] + TOL for i in range(len(lows) - 1)):
                anomaly('class lower bounds not monotonic', lab, (cu, el, lows))
            if 'matig' in cl:
                mu = fl(cl['matig'][0]['BovengrensWaarde'])
                if mu is not None and abs(mu - ol) > 1e-6:
                    anomaly("matig upper bound != goed lower bound (gap/overlap)", lab, (cu, el, mu, ol))
            if el in EKR_EL and not (0 <= val <= 1):
                anomaly('EKR goal outside 0..1', lab, (cu, el, val))
        else:
            ups = [(c, fl(cl[c][0]['BovengrensWaarde'])) for c in ['goed', 'matig', 'ontoereikend', 'slecht'] if c in cl]
            ups = [(c, v) for c, v in ups if v is not None]
            if any(ups[i][1] > ups[i + 1][1] + TOL for i in range(len(ups) - 1)):
                anomaly('class upper bounds not monotonic', lab, (cu, el, ups))
            if 'matig' in cl:
                ml = fl(cl['matig'][0]['OndergrensWaarde'])
                if ml is not None and abs(ml - ou) > 1e-6:
                    anomaly("matig lower bound != goed upper bound (gap/overlap)", lab, (cu, el, ml, ou))
            if fl(g['OndergrensWaarde']) != 0.0:
                anomaly('goed lower bound not 0 (P/N/Cl)', lab, (cu, el, g['OndergrensWaarde']))
        goals[(cu, el)] = val
    return goals, meta


G = {}
M = {}
for s in sets:
    G[s['label']], M[s['label']] = build(s)
    s['classes'] = collections.Counter(r['Classificatie'] for r in s['rows'] if r['KRWkwaliteitselementCode'] in ALL_EL)

P('## 1. Goal definition verification: anomalies per goal set (count of body x element goals)')
labs = [s['label'] for s in sets]
table(['anomaly'] + labs, [[k] + [ANOM[k].get(l, 0) for l in labs] for k in sorted(ANOM)] or [['(none)'] + [0] * len(labs)])
for k, ex in ANOM_EX.items():
    P(f'  examples "{k}":', ex[:3])
P('Classes present in analysed rows:', {l: dict(SETBY[l]['classes']) for l in labs[:1] + labs[-1:]})
P('Number of goals (body x element) per set:')
table(['set'] + ALL_EL, [[l] + [sum(1 for (c, e) in G[l] if e == el) for el in ALL_EL] for l in labs])
sym = collections.Counter()
for s in sets:
    for r in s['rows']:
        if r['KRWkwaliteitselementCode'] in ALL_EL and r['Classificatie'] == 'goed':
            sym[('EKR' if r['KRWkwaliteitselementCode'] in EKR_EL else r['KRWkwaliteitselementCode'], r['OndergrensSymbool'], r['BovengrensSymbool'])] += 1
P("Symbols on 'goed' rows (element group, lower symbol, upper symbol):", dict(sym))
P('')
ub = collections.Counter()
for r in SETBY[labs[-1]]['rows']:
    if r['KRWkwaliteitselementCode'] in EKR_EL and r['Classificatie'] == 'goed':
        ub[(r['WaterlichaamKRWstatus'], r['BovengrensWaarde'], r['BovengrensSymbool'])] += 1
P("Latest set, EKR 'goed' upper bound (status, value, symbol):", dict(ub))
P('')

# ---------------------------------------------------------------- OWL: predecessor
pred = collections.defaultdict(set)
for f in sorted(glob.glob(os.path.join(ROOT, 'WKP_download_OWL_*/WKP_KRW-oppervlaktewaterlichamen_Nederland_*.csv'))):
    for r in rd(f):
        cu = r['WaterlichaamCode'].upper()
        for p in re.split(r'[|,;]', r['VoorgangerCode']):
            if p.strip():
                pred[cu].add(p.strip().upper())
P(f'## OWL files: bodies with a VoorgangerCode in any year: {len(pred)}')
P('')

# ---------------------------------------------------------------- long CSV
with open(os.path.join(OUT, 'doelen_ekr_long.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['waterlichaam_code', 'waterlichaam_naam', 'beheerder', 'krw_status', 'watertype', 'element', 'goal_set_year', 'goal_value', 'goal_set_files', 'eenheid'])
    unit = {'FYTOPL': 'EKR', 'MAFAUNA': 'EKR', 'OVWFLORA': 'EKR', 'VIS': 'EKR', 'Ptot': 'mg/l P', 'Ntot': 'mg/l N'}
    n = 0
    for s in sets:
        l = s['label']
        for (cu, el), v in sorted(G[l].items()):
            if el in EKR_EL + PN_EL:
                m = M[l][cu]
                w.writerow([m['code'], m['naam'], m['beheerder'], m['status'], m['watertype'], el, l, v, s['filespan'], unit[el]])
                n += 1
P(f'doelen_ekr_long.csv rows: {n}\n')


# ---------------------------------------------------------------- comparisons
def norm_name(n):
    return re.sub(r'[^a-z0-9]', '', n.lower())


def body_map(la, lb):
    """Map code in B -> code in A for bodies not matched by code. 1) OWL VoorgangerCode, 2) unique (name, beheerder) match
    (1:1 on both sides). Returns {new: (old, how)}."""
    MA, MB = M[la], M[lb]
    ua = set(MA) - set(MB)
    ub = set(MB) - set(MA)
    mp = {}
    for cu in sorted(ub):
        for p in pred.get(cu, ()):
            if p in ua:
                mp[cu] = (p, 'voorganger')
                break
    ua2 = ua - {o for o, h in mp.values()}
    ub2 = ub - set(mp)
    ga = collections.defaultdict(list)
    gb = collections.defaultdict(list)
    for c in ua2:
        ga[(norm_name(MA[c]['naam']), MA[c]['beheerder'])].append(c)
    for c in ub2:
        gb[(norm_name(MB[c]['naam']), MB[c]['beheerder'])].append(c)
    for k, lst in gb.items():
        if len(lst) == 1 and len(ga.get(k, [])) == 1:
            mp[lst[0]] = (ga[k][0], 'naam')
    return mp


def compare(la, lb, use_names=True):
    A, B, MA, MB = G[la], G[lb], M[la], M[lb]
    bodiesA = {c for c, e in A}
    bodiesB = {c for c, e in B}
    mp = body_map(la, lb) if use_names else {}
    if use_names:
        mp = {k: v for k, v in mp.items()}
    else:
        mp = {k: v for k, v in body_map(la, lb).items() if v[1] == 'voorganger'}
    inv = {o: n for n, (o, h) in mp.items()}
    out = []
    nvia = collections.Counter(h for o, h in mp.values())
    keys = set()
    for (cu, el) in A:
        keys.add((inv.get(cu, cu), el, cu))      # (code in B space, element, code in A)
    for (cu, el) in B:
        keys.add((cu, el, mp[cu][0] if cu in mp else cu))
    for cb, el, ca in keys:
        sgn = SIGN[el]
        a, b = A.get((ca, el)), B.get((cb, el))
        meta = MB.get(cb) or MA.get(ca)
        rec = dict(code=cb, code_a=ca, el=el, a=a, b=b, status=meta['status'], beheerder=meta['beheerder'], naam=meta['naam'], watertype=meta['watertype'],
                   renamed=(cb != ca))
        if a is not None and b is not None:
            d = b - a
            rec['cls'] = 'equal' if abs(d) <= TOL else ('up' if sgn * d > 0 else 'down')
            rec['delta'] = d
            rec['rel'] = (d / a * 100) if a else None
        elif b is not None:
            rec['cls'] = 'appeared_new_body' if (cb not in mp and cb not in {c for c, e in A}) else 'appeared_new_element'
        else:
            rec['cls'] = 'disappeared_body_gone' if (inv.get(ca, ca) not in bodiesB) else 'disappeared_element_gone'
        out.append(rec)
    return out, dict(nvia)


CLS = ['up', 'down', 'equal', 'appeared_new_body', 'appeared_new_element', 'disappeared_body_gone', 'disappeared_element_gone']
STK = ['delta_median_changed', 'delta_p10', 'delta_p90', 'delta_median_up', 'delta_median_down', 'rel_median_changed_pct']


def stats(recs):
    ch = [r for r in recs if r['cls'] in ('up', 'down')]
    d = [r['delta'] for r in ch]
    dr = [r['rel'] for r in ch if r['rel'] is not None]
    du = [r['delta'] for r in recs if r['cls'] == 'up']
    dd = [r['delta'] for r in recs if r['cls'] == 'down']
    cnt = collections.Counter(r['cls'] for r in recs)
    o = {c: cnt.get(c, 0) for c in CLS}
    o.update(n_total=len(recs), n_both=cnt['up'] + cnt['down'] + cnt['equal'],
             delta_median_changed=rnd(median(d)) if d else None, delta_p10=rnd(q(d, .1)), delta_p90=rnd(q(d, .9)),
             delta_median_up=rnd(median(du)) if du else None, delta_median_down=rnd(median(dd)) if dd else None,
             rel_median_changed_pct=rnd(median(dr), 1) if dr else None)
    return o


pairs = [(labs[i], labs[i + 1]) for i in range(len(labs) - 1)]
SGBP2, SGBP3, LAST = '2015', '2021', labs[-1]
for a, b in [(SGBP2, SGBP3), (SGBP2, LAST), (SGBP3, LAST), ('2014', SGBP3), ('2013', LAST)]:
    if a in SETBY and b in SETBY and (a, b) not in pairs:
        pairs.append((a, b))
rows_out = []
COMP = {}
GROUPS = [('ALL_EKR', EKR_EL)] + [(e, [e]) for e in ALL_EL]
for la, lb in pairs:
    recs, nvia = compare(la, lb)
    COMP[(la, lb)] = recs
    COMP[(la, lb, 'via')] = nvia
    COMP[(la, lb, 'codeonly')] = compare(la, lb, use_names=False)[0]
    for gname, els in GROUPS:
        sub = [r for r in recs if r['el'] in els]
        for dim, keyf in [('all', lambda r: 'all'), ('krw_status', lambda r: r['status']), ('beheerder', lambda r: r['beheerder'])]:
            gs = collections.defaultdict(list)
            for r in sub:
                gs[keyf(r)].append(r)
            for gv, lst in sorted(gs.items()):
                st = stats(lst)
                rows_out.append([la, lb, dim, gv, gname] + [st[k] for k in ['n_total', 'n_both'] + CLS + STK])
hdr = ['from_set', 'to_set', 'dimension', 'group', 'element_group', 'n_total', 'n_both'] + CLS + STK
with open(os.path.join(OUT, 'doelen_changes_summary.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(hdr)
    w.writerows(rows_out)

P('## 2. Changes between goal sets (body x element goals; ALL_EKR = four biological elements pooled)')
P('delta = new - old in the element unit (EKR; mg/l for Ptot/Ntot/Cl; m for ZICHT). up = more ambitious (EKR/ZICHT higher, Ptot/Ntot/Cl lower).')
for la, lb in pairs:
    recs = COMP[(la, lb)]
    P(f'### {la} -> {lb}   (bodies matched without identical code: {COMP[(la, lb, "via")]})')
    trows = []
    for gname, els in GROUPS:
        st = stats([r for r in recs if r['el'] in els])
        trows.append([gname] + [st[k] for k in ['n_both'] + CLS + STK])
    table(['element', 'n in both'] + CLS + ['median d (changed)', 'p10', 'p90', 'median d up', 'median d down', 'median rel %'], trows)
for la, lb in [(SGBP2, SGBP3), (SGBP3, LAST), (SGBP2, LAST)]:
    if (la, lb) not in COMP:
        continue
    recs = [r for r in COMP[(la, lb)] if r['el'] in EKR_EL]
    P(f'### {la} -> {lb}: EKR elements by KRW status')
    trows = []
    for stt in ['Natuurlijk', 'Sterk veranderd', 'Kunstmatig']:
        st = stats([r for r in recs if r['status'] == stt])
        trows.append([stt] + [st[k] for k in ['n_both'] + CLS[:3] + ['delta_median_changed', 'delta_p10', 'delta_p90']])
    table(['status', 'n in both', 'up', 'down', 'equal', 'median d', 'p10', 'p90'], trows)
    P(f'### {la} -> {lb}: EKR elements by waterbeheerder')
    bs = collections.defaultdict(list)
    for r in recs:
        bs[r['beheerder']].append(r)
    trows = []
    for b, lst in sorted(bs.items(), key=lambda kv: -len(kv[1])):
        st = stats(lst)
        ch = st['up'] + st['down']
        trows.append([b, st['n_both'], st['up'], st['down'], st['equal'], st['appeared_new_body'] + st['appeared_new_element'],
                      st['disappeared_body_gone'] + st['disappeared_element_gone'], rnd(st['down'] / ch * 100, 0) if ch else None, st['delta_median_changed']])
    table(['beheerder', 'n both', 'up', 'down', 'equal', 'appeared', 'disappeared', '% down of changed', 'median d'], trows)
    P(f'### {la} -> {lb}: Ptot/Ntot/Cl/ZICHT by KRW status')
    trows = []
    for el in PN_EL + ['Cl', 'ZICHT']:
        for stt in ['Natuurlijk', 'Sterk veranderd', 'Kunstmatig']:
            st = stats([r for r in COMP[(la, lb)] if r['el'] == el and r['status'] == stt])
            trows.append([el, stt, st['n_both'], st['up'], st['down'], st['equal'], st['rel_median_changed_pct']])
    table(['element', 'status', 'n both', 'up', 'down', 'equal', 'median rel % (changed)'], trows)

P('### Body matching between sets (VoorgangerCode: none present in OWL files; fallback = unique name+beheerder)')
trows = []
for la, lb in pairs:
    recs = COMP[(la, lb)]
    co = COMP[(la, lb, 'codeonly')]
    nb_new0 = len({r['code'] for r in co if r['cls'] == 'appeared_new_body'})
    nb_gone0 = len({r['code_a'] for r in co if r['cls'] == 'disappeared_body_gone'})
    nb_new = len({r['code'] for r in recs if r['cls'] == 'appeared_new_body'})
    nb_gone = len({r['code_a'] for r in recs if r['cls'] == 'disappeared_body_gone'})
    trows.append([f'{la}->{lb}', nb_new0, nb_gone0, COMP[(la, lb, 'via')].get('naam', 0), nb_new, nb_gone])
table(['pair', 'new codes (code-only match)', 'old codes gone (code-only)', 'recovered by name+beheerder', 'still new', 'still gone'], trows)

P('### KRW status changes of the same body between sets')
trows = []
for la, lb in pairs:
    ch = collections.Counter((M[la][c]['status'], M[lb][c]['status']) for c in M[la] if c in M[lb] and M[la][c]['status'] != M[lb][c]['status'])
    trows.append([f'{la}->{lb}', dict(ch) or 'none'])
table(['pair', 'status transitions (old, new): n bodies'], trows)

# ---------------------------------------------------------------- Q3
P('## 3. EKR goals vs 0.6 by KRW status')


def ekr_goals(l):
    return [(c, e, v) for (c, e), v in G[l].items() if e in EKR_EL]


for l in sorted({SGBP2, SGBP3, LAST}, key=int):
    gl = ekr_goals(l)
    P(f'### Set {l}')
    trows = []
    for stt in ['Natuurlijk', 'Sterk veranderd', 'Kunstmatig']:
        v = [x for c, e, x in gl if M[l][c]['status'] == stt]
        if not v:
            continue
        trows.append([stt, len(v), sum(1 for x in v if abs(x - 0.6) < 1e-9), sum(1 for x in v if x > 0.6 + 1e-9), sum(1 for x in v if x < 0.6 - 1e-9),
                      rnd(min(v)), rnd(q(v, .1)), rnd(q(v, .25)), rnd(median(v)), rnd(q(v, .75)), rnd(max(v))])
    table(['status', 'n goals', '= 0.60', '> 0.60', '< 0.60', 'min', 'p10', 'p25', 'median', 'p75', 'max'], trows)
    P('By element x status:')
    trows = []
    for e in EKR_EL:
        for stt in ['Natuurlijk', 'Sterk veranderd', 'Kunstmatig']:
            v = [x for c, el, x in gl if el == e and M[l][c]['status'] == stt]
            if not v:
                continue
            low = [0.6 - x for x in v if x < 0.6 - 1e-9]
            trows.append([e, stt, len(v), len(low), rnd(len(low) / len(v) * 100, 0), rnd(median(low)) if low else None,
                          rnd(q(low, .9)) if low else None, rnd(min(v)), rnd(median(v))])
    table(['element', 'status', 'n', 'n <0.6', '% <0.6', 'median shortfall', 'p90 shortfall', 'min goal', 'median goal'], trows)
    cnt = collections.Counter(round(x, 2) for c, e, x in gl)
    P('Most common goal values (all EKR, all statuses):', cnt.most_common(12))
    cntn = collections.Counter(round(x, 2) for c, e, x in gl if M[l][c]['status'] == 'Natuurlijk')
    P('Natural bodies: goal value counts:', dict(cntn))
    P('Histogram of EKR goals for HMWB / artificial:')
    trows = []
    for lo, hi in [(0, .2), (.2, .3), (.3, .4), (.4, .5), (.5, .6)]:
        row = [f'[{lo},{hi})']
        for stt in ['Sterk veranderd', 'Kunstmatig']:
            v = [x for c, e, x in gl if M[l][c]['status'] == stt]
            row.append(sum(1 for x in v if lo - 1e-9 <= x < hi - 1e-9 and abs(x - .6) > 1e-9))
        trows.append(row)
    row = ['=0.60']
    for stt in ['Sterk veranderd', 'Kunstmatig']:
        row.append(sum(1 for c, e, x in gl if M[l][c]['status'] == stt and abs(x - .6) < 1e-9))
    trows.append(row)
    row = ['>0.60']
    for stt in ['Sterk veranderd', 'Kunstmatig']:
        row.append(sum(1 for c, e, x in gl if M[l][c]['status'] == stt and x > .6 + 1e-9))
    trows.append(row)
    table(['bin', 'Sterk veranderd', 'Kunstmatig'], trows)
    bd = {c for c, e, x in gl if x < .6 - 1e-9 and M[l][c]['status'] != 'Natuurlijk'}
    allb = {c for c, e, x in gl if M[l][c]['status'] != 'Natuurlijk'}
    P(f'HMWB/artificial bodies with >=1 EKR goal below 0.6: {len(bd)} of {len(allb)} (with any EKR goal)')
    nn = [(c, e, x) for c, e, x in gl if M[l][c]['status'] == 'Natuurlijk' and abs(x - .6) > 1e-9]
    P(f'Natural-status goals not equal to 0.60: {len(nn)}; examples: {[(M[l][c]["code"], e, x) for c, e, x in nn[:6]]}')
    P('')
P('Share of HMWB+artificial EKR goals below 0.60 per goal set:')
trows = []
for s in sets:
    l = s['label']
    gl = ekr_goals(l)
    v = [x for c, e, x in gl if M[l][c]['status'] != 'Natuurlijk']
    nat = [x for c, e, x in gl if M[l][c]['status'] == 'Natuurlijk']
    trows.append([l, s['filespan'], len(v), sum(1 for x in v if x < .6 - 1e-9), rnd(sum(1 for x in v if x < .6 - 1e-9) / len(v) * 100, 1), rnd(median(v)), len(nat), sum(1 for x in nat if abs(x - .6) < 1e-9)])
table(['set', 'files', 'n HMWB/art goals', 'n <0.6', '% <0.6', 'median goal', 'n natural goals', 'n natural =0.6'], trows)
P('Median EKR goal per element for non-natural bodies per set:')
table(['set'] + EKR_EL, [[s['label']] + [rnd(median([v for (c, e), v in G[s['label']].items() if e == el and M[s['label']][c]['status'] != 'Natuurlijk'])) for el in EKR_EL] for s in sets])

# ---------------------------------------------------------------- Q4
P('## 4. Goal change vs earlier measured EKR')
meas = {}
for y in (2009, 2019, 2020, 2021):
    f = find(f'WKP_download_oordelen_*/WKP_KRW-toestandsoordelen-beknopt_Nederland_{y}_*.csv')
    d = {}
    dup = 0
    for r in rd(f, ['WaterlichaamCode', 'KRWkwaliteitselementCode', 'Classificatie', 'BepalendKental', 'EenheidCode', 'HoedanigheidCode', 'Einddatum']):
        el = r['KRWkwaliteitselementCode']
        if el not in EKR_EL:
            continue
        key = (r['WaterlichaamCode'].upper(), el)
        v = fl(r['BepalendKental']) if r['HoedanigheidCode'] == 'EKR' else None
        rec = (v, r['Classificatie'], r['Einddatum'])
        if key in d:
            dup += 1
            if v is None or (d[key][0] is not None and d[key][2] >= r['Einddatum']):
                continue
        d[key] = rec
    meas[y] = d
    P(f'Assessment file {y}: EKR-element rows {len(d)}, with numeric EKR {sum(1 for v in d.values() if v[0] is not None)}, duplicate rows resolved {dup}')
P('Note: 2014-2019 assessment files carry class only (BepalendKental empty or 0); numeric EKR exists for 2009, 2020, 2021+.\n')
CLASSNUM = {'Slecht': 1, 'Ontoereikend': 2, 'Matig': 3, 'Goed': 4, 'Zeer goed': 5}


def q4(la, lb, mfile, title, value_field=0):
    recs = [r for r in COMP[(la, lb)] if r['el'] in EKR_EL and r['cls'] in ('up', 'down', 'equal')]
    rows = []
    for r in recs:
        m = meas[mfile].get((r['code_a'] if mfile in (2009, 2019) else r['code'], r['el']))
        if not m:
            continue
        mv = m[0] if value_field == 0 else CLASSNUM.get(m[1])
        if mv is None:
            continue
        rows.append(dict(r, meas=mv))
    P(f'### {title}: goals {la} -> {lb}, measured = assessment file {mfile}; matched n = {len(rows)} of {len(recs)}')
    for lab_, flt in [('all', lambda r: True), ('natural', lambda r: r['status'] == 'Natuurlijk'), ('HMWB+artificial', lambda r: r['status'] != 'Natuurlijk')]:
        sub = [r for r in rows if flt(r)]
        if not sub:
            continue
        a = [r['meas'] for r in sub]
        d = [r['delta'] for r in sub]
        P(f'{lab_}: n={len(sub)}  Spearman(measured, delta goal)={rnd(spearman(a, d))}  95% bootstrap CI={spearman_ci(a, d)}')
    if value_field == 0:
        trows = []
        for lab_, flt in [('natural', lambda r: r['status'] == 'Natuurlijk'), ('HMWB+artificial', lambda r: r['status'] != 'Natuurlijk')]:
            for cls in ['down', 'equal', 'up']:
                sub = [r for r in rows if flt(r) and r['cls'] == cls]
                if not sub:
                    continue
                trows.append([lab_, cls, len(sub), rnd(median([r['a'] for r in sub])), rnd(median([r['b'] for r in sub])), rnd(median([r['meas'] for r in sub])),
                              rnd(sum(1 for r in sub if r['meas'] >= r['a'] - 1e-9) / len(sub) * 100, 0), rnd(sum(1 for r in sub if r['meas'] >= r['b'] - 1e-9) / len(sub) * 100, 0)])
        table(['group', 'goal change', 'n', 'median old goal', 'median new goal', 'median measured', '% measured >= old goal', '% measured >= new goal'], trows)
        trows = []
        for lab_, flt in [('natural', lambda r: r['status'] == 'Natuurlijk'), ('HMWB+artificial', lambda r: r['status'] != 'Natuurlijk')]:
            sub = [r for r in rows if flt(r)]
            for nm, cond in [('measured < old goal (failing)', lambda r: r['meas'] < r['a'] - 1e-9), ('measured >= old goal (meeting)', lambda r: r['meas'] >= r['a'] - 1e-9)]:
                s2 = [r for r in sub if cond(r)]
                if s2:
                    trows.append([lab_, nm, len(s2), rnd(sum(1 for r in s2 if r['cls'] == 'down') / len(s2) * 100, 1), rnd(sum(1 for r in s2 if r['cls'] == 'up') / len(s2) * 100, 1)])
        table(['group', 'old goal vs measured', 'n', '% goal lowered', '% goal raised'], trows)
        trows = []
        for lo, hi in [(-9, -.3), (-.3, -.15), (-.15, -.05), (-.05, 1e-9), (1e-9, 9)]:
            sub = [r for r in rows if r['status'] != 'Natuurlijk' and lo <= r['meas'] - r['a'] < hi]
            if sub:
                trows.append([f'[{lo},{hi})', len(sub), rnd(sum(1 for r in sub if r['cls'] == 'down') / len(sub) * 100, 1), rnd(median([r['delta'] for r in sub]), 3)])
        P('HMWB+artificial: lowering rate by gap (measured minus old goal):')
        table(['gap bin', 'n', '% lowered', 'median delta'], trows)
        lw = [r for r in rows if r['cls'] == 'down' and r['status'] != 'Natuurlijk']
        if lw:
            diff = [r['b'] - r['meas'] for r in lw]
            P(f'HMWB+artificial lowered goals: new goal minus measured EKR: median {rnd(median(diff))}, p10 {rnd(q(diff, .1))}, p90 {rnd(q(diff, .9))}; '
              f'new goal <= measured in {rnd(sum(1 for d in diff if d <= 1e-9) / len(diff) * 100, 0)}%; '
              f'new goal within 0.1 below measured in {rnd(sum(1 for d in diff if -0.1 <= d <= 1e-9) / len(diff) * 100, 0)}%')
        un = [r for r in rows if r['cls'] == 'equal' and r['status'] != 'Natuurlijk' and r['meas'] < r['a'] - 1e-9]
        P(f'HMWB+artificial, goal unchanged but measured below goal (failing, not lowered): n={len(un)}')
        P('')
    return rows


r1 = q4(SGBP2, SGBP3, 2020, 'Q4a primary (measured period 2009-2019)')
q4(SGBP2, LAST, 2020, 'Q4b (goals to latest set; measured 2009-2019)')
q4(SGBP2, SGBP3, 2009, 'Q4c sensitivity: oldest numeric assessment (2003-2008)')
q4(SGBP2, SGBP3, 2019, 'Q4d sensitivity: class (1=slecht..5) in 2019 assessment instead of numeric EKR', value_field=1)
q4(SGBP2, SGBP3, 2021, 'Q4e sensitivity: assessment file 2021 (period 2010-2020)')
P('Primary Q4a by element (HMWB+artificial): n, % lowered, Spearman(measured, delta)')
trows = []
for e in EKR_EL:
    sub = [r for r in r1 if r['el'] == e and r['status'] != 'Natuurlijk']
    if sub:
        trows.append([e, len(sub), rnd(sum(1 for r in sub if r['cls'] == 'down') / len(sub) * 100, 1), rnd(spearman([r['meas'] for r in sub], [r['delta'] for r in sub]))])
table(['element', 'n', '% lowered', 'Spearman'], trows)
with open(os.path.join(OUT, 'q4_link_table.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['waterlichaam_code', 'naam', 'beheerder', 'krw_status', 'element', f'goal_{SGBP2}', f'goal_{SGBP3}', 'delta', 'class', 'measured_ekr_2009_2019', 'code_in_older_set'])
    for r in r1:
        w.writerow([r['code'], r['naam'], r['beheerder'], r['status'], r['el'], r['a'], r['b'], rnd(r['delta'], 4), r['cls'], r['meas'], r['code_a']])

with open(os.path.join(OUT, 'report_tables.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(REPORT))
print('done')

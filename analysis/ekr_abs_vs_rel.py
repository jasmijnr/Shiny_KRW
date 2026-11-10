"""
EKR absolute vs. relative-to-goal (feasibility check for the 'ranking flip' plot).

For reporting year 2025, per water body x biological element (FYTOPL, MAFAUNA, OVWFLORA, VIS):
  - ekr      : measured EKR (BepalendKental, condensed assessment file, HoedanigheidCode == 'EKR')
  - goal     : lower bound of class 'goed' in the 2025 goal set (doelen file)
  - ratio    : ekr / goal          (>= 1 means 'goed' reached)
  - gap      : ekr - goal
  - rank_abs : rank on ekr (1 = highest) within element
  - rank_rel : rank on ratio (1 = highest) within element

Run:  python -I analysis/ekr_abs_vs_rel.py   (from project root)
Out:  analysis/output/ekr_abs_vs_rel_2025.csv  + summary printed to stdout
"""
import csv, glob, os, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YEAR = "2025"
ELEMENTS = {"FYTOPL", "MAFAUNA", "OVWFLORA", "VIS"}


def rows(pattern):
    f = glob.glob(os.path.join(ROOT, pattern))[0]
    with open(f, encoding="utf-8-sig", newline="") as fh:
        yield from csv.DictReader(fh, delimiter=";")


goals, meta = {}, {}
for r in rows(f"WKP_download_doelen_*/WKP_KRW-doelen_Nederland_{YEAR}_*.csv"):
    if r["KRWkwaliteitselementCode"] in ELEMENTS and r["Classificatie"].lower() == "goed":
        k = (r["WaterlichaamCode"].upper(), r["KRWkwaliteitselementCode"])
        goals[k] = float(r["OndergrensWaarde"])
        meta[k[0]] = (r["WaterlichaamNaam"], r["WaterbeheerderNaam"], r["WaterlichaamKRWstatus"],
                      r["WaterlichaamKRWwatertypeCode"])

ekr = {}
for r in rows(f"WKP_download_oordelen_*/WKP_KRW-toestandsoordelen-beknopt_Nederland_{YEAR}_*.csv"):
    if r["KRWkwaliteitselementCode"] in ELEMENTS and r["HoedanigheidCode"] == "EKR" and r["BepalendKental"] not in ("", "-"):
        ekr[(r["WaterlichaamCode"].upper(), r["KRWkwaliteitselementCode"])] = (float(r["BepalendKental"]), r["Classificatie"])

out = []
for k, (v, cls) in ekr.items():
    if k in goals and goals[k] > 0:
        n, b, s, t = meta[k[0]]
        out.append(dict(waterlichaam_code=k[0], naam=n, beheerder=b, krw_status=s, watertype=t, element=k[1],
                        ekr=v, goal=goals[k], ratio=round(v / goals[k], 4), gap=round(v - goals[k], 4), klasse=cls))

for el in sorted(ELEMENTS):
    sub = [o for o in out if o["element"] == el]
    for key, rk in (("ekr", "rank_abs"), ("ratio", "rank_rel")):
        for i, o in enumerate(sorted(sub, key=lambda o: -o[key]), 1):
            o[rk] = i

os.makedirs(os.path.join(ROOT, "analysis", "output"), exist_ok=True)
with open(os.path.join(ROOT, "analysis", "output", f"ekr_abs_vs_rel_{YEAR}.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys()), delimiter=";")
    w.writeheader(); w.writerows(out)

print(f"matched pairs: {len(out)} (ekr values {len(ekr)}, goals {len(goals)})")
for el in sorted(ELEMENTS):
    sub = [o for o in out if o["element"] == el]
    n = len(sub)
    shift = [abs(o["rank_abs"] - o["rank_rel"]) for o in sub]
    low_abs_ok = [o for o in sub if o["ekr"] < 0.6 and o["ratio"] >= 1]   # 'goed' only thanks to lowered goal
    nat = [o["goal"] for o in sub if o["krw_status"].lower().startswith("natuurlijk")]
    hm = [o["goal"] for o in sub if not o["krw_status"].lower().startswith("natuurlijk")]
    # Spearman rank correlation abs vs rel
    d2 = sum((o["rank_abs"] - o["rank_rel"]) ** 2 for o in sub)
    rho = 1 - 6 * d2 / (n * (n * n - 1)) if n > 2 else float("nan")
    print(f"\n{el}: n={n}  goal median nat={st.median(nat) if nat else '-'} hmwb/kunstm={st.median(hm) if hm else '-'} "
          f"(min {min(hm) if hm else '-'})")
    print(f"  reaches goal: {sum(o['ratio'] >= 1 for o in sub)}  |  of which EKR < 0.6: {len(low_abs_ok)}")
    print(f"  median |rank shift| = {st.median(shift)}  max = {max(shift)}  spearman rho = {rho:.2f}")

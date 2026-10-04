"""Div (दिव्) 10-year financial model. All money in ₹ lakh. Year 1 = FY2027-28 (Apr 2027 - Mar 2028).
Run: python3 plan/div_model.py  -> prints tables and writes plan/div_model.csv"""
import csv, pathlib

YEARS = 10
FY = [f"FY{27 + i}-{28 + i}" for i in range(YEARS)]

# Year-1 revenue by vertical and year-on-year growth for years 2..10 (%)
# Growth bands: first three growth years (FY28-29..FY30-31) 20-25%, next three (FY31-32..FY33-34) 25-30%,
# then market-led (base case below; MARKET_CASES scales those last three years).
# Home base Bhubaneswar; Rourkela opens year 2, Sambalpur year 3; Raipur and Ranchi in years 4-6.
VERT = {
    "Consulting":           (90,  [24, 25, 25, 30, 30, 29, 26, 25, 24]),
    "Integration":          (120, [20, 21, 22, 27, 27, 27, 22, 21, 20]),
    "Facility Maintenance": (25,  [25, 26, 26, 30, 30, 30, 28, 27, 26]),
    "Training":             (15,  [22, 24, 25, 30, 30, 30, 26, 25, 24]),
}
MARKET_CASES = {"slow market": -8, "base": 0, "strong market": 6}   # points added to years 8-10 growth
# contribution margin after direct cost (project staff, materials, subcontract), %
MARGIN = {"Consulting": .55, "Integration": .22, "Facility Maintenance": .40, "Training": .60}
OVERHEAD_Y1 = 48                       # leadership, office, marketing, DC R&D lab, wellness programme
OVERHEAD_G = [16, 16, 15, 22, 22, 22, 18, 18, 18]  # % a year; steps up when Raipur and Ranchi open
REV_PER_HEAD_Y1, REV_PER_HEAD_G = 20.8, .04         # ₹ lakh revenue per employee
DEP_Y1, DEP_G = 8, .25
INTEREST = [4.5] * 3 + [3.0] * 2 + [0] * 5  # ₹50 lakh working-capital limit, repaid from year 4
TAX = .2517                                   # section 115BAA rate
EQUITY, LOAN = 100, 50

def run(shift=0):
    rev = {k: [] for k in VERT}
    for k, (y1, g) in VERT.items():
        v = y1
        for i in range(YEARS):
            rev[k].append(v)
            if i < YEARS - 1:
                v = v * (1 + (g[i] + (shift if i >= 6 else 0)) / 100)
    rows, cum_pat, oh = [], 0, OVERHEAD_Y1
    for i in range(YEARS):
        if i:
            oh *= 1 + OVERHEAD_G[i - 1] / 100
        r = {k: rev[k][i] for k in VERT}
        total = sum(r.values())
        contrib = sum(r[k] * MARGIN[k] for k in VERT)
        ebitda = contrib - oh
        dep = DEP_Y1 * (1 + DEP_G) ** i
        pat = (ebitda - dep - INTEREST[i]) * (1 - TAX)
        cum_pat += pat
        heads = round(total / (REV_PER_HEAD_Y1 * (1 + REV_PER_HEAD_G) ** i))
        rows.append(dict(fy=FY[i], **r, total=total, ebitda=ebitda, pat=pat, cum_pat=cum_pat,
                         ebitda_m=ebitda / total, pat_m=pat / total, heads=heads))
    for i, r in enumerate(rows):
        r["g_rev"] = (r["total"] / rows[i - 1]["total"] - 1) * 100 if i else None
        r["g_pat"] = (r["pat"] / rows[i - 1]["pat"] - 1) * 100 if i else None
    return rows

rows = run()

print(f"{'FY':9}{'Cons':>8}{'Integ':>8}{'FM':>8}{'Train':>8}{'Total':>9}{'g%':>6}{'EBITDA':>8}{'EB%':>6}{'PAT':>8}{'PAT%':>6}{'gPAT':>6}{'cumPAT':>8}{'Heads':>7}")
for r in rows:
    print(f"{r['fy']:9}{r['Consulting']:8.0f}{r['Integration']:8.0f}{r['Facility Maintenance']:8.0f}{r['Training']:8.0f}{r['total']:9.0f}"
          f"{(r['g_rev'] or 0):6.0f}{r['ebitda']:8.0f}{r['ebitda_m'] * 100:6.1f}{r['pat']:8.1f}{r['pat_m'] * 100:6.1f}{(r['g_pat'] or 0):6.0f}{r['cum_pat']:8.0f}{r['heads']:7d}")
band = lambda lo, hi, rs: all(lo <= r["g_rev"] <= hi for r in rs)
print("revenue growth 20-25% in FY28-29..FY30-31:", band(20, 25, rows[1:4]))
print("revenue growth 25-30% in FY31-32..FY33-34:", band(25, 30, rows[4:7]))
for name, shift in MARKET_CASES.items():
    rs = run(shift)
    print(f"{name:14} year-10 revenue {rs[-1]['total']:7.0f}  PAT {rs[-1]['pat']:6.0f}  heads {rs[-1]['heads']}")
pb = next((r["fy"] for r in rows if r["cum_pat"] >= EQUITY + LOAN), None)
print("payback of ₹150 lakh capital by cumulative PAT in:", pb)
with open(pathlib.Path(__file__).parent / "div_model.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["FY"] + list(VERT) + ["Total revenue", "EBITDA", "PAT", "Revenue growth %", "PAT growth %", "Headcount"])
    for r in rows:
        w.writerow([r["fy"]] + [round(r[k], 1) for k in VERT] + [round(r["total"], 1), round(r["ebitda"], 1), round(r["pat"], 1),
                   "" if r["g_rev"] is None else round(r["g_rev"], 1), "" if r["g_pat"] is None else round(r["g_pat"], 1), r["heads"]])

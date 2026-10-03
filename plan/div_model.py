"""Div (दिव्) 10-year financial model. All money in ₹ lakh. Year 1 = FY2027-28 (Apr 2027 - Mar 2028).
Run: python3 plan/div_model.py  -> prints tables and writes plan/div_model.csv"""
import csv, pathlib

YEARS = 10
FY = [f"FY{27 + i}-{28 + i}" for i in range(YEARS)]

# Year-1 revenue by vertical and year-on-year growth for years 2..10 (%)
VERT = {
    "Consulting":           (90,  [45, 42, 40, 38, 35, 34, 33, 32, 32]),
    "Integration":          (120, [50, 45, 42, 40, 36, 34, 33, 32, 31]),
    "Facility Maintenance": (25,  [70, 60, 50, 45, 40, 38, 35, 34, 33]),
    "Training":             (15,  [60, 50, 45, 40, 36, 34, 32, 31, 30]),
}
# contribution margin after direct cost (project staff, materials, subcontract), %
MARGIN = {"Consulting": .55, "Integration": .22, "Facility Maintenance": .40, "Training": .60}
OVERHEAD_Y1, OVERHEAD_G = 48, .28      # leadership, office, marketing, DC R&D lab, wellness programme
DEP_Y1, DEP_G = 8, .25
INTEREST = [4.5] * 3 + [3.0] * 2 + [0] * 5  # ₹50 lakh working-capital limit, repaid from year 4
TAX = .2517                                   # section 115BAA rate
EQUITY, LOAN = 100, 50

rev = {k: [] for k in VERT}
for k, (y1, g) in VERT.items():
    v = y1
    for i in range(YEARS):
        rev[k].append(v)
        if i < YEARS - 1:
            v = v * (1 + g[i] / 100)

rows = []
cum_pat = 0
for i in range(YEARS):
    r = {k: rev[k][i] for k in VERT}
    total = sum(r.values())
    contrib = sum(r[k] * MARGIN[k] for k in VERT)
    oh = OVERHEAD_Y1 * (1 + OVERHEAD_G) ** i
    ebitda = contrib - oh
    dep = DEP_Y1 * (1 + DEP_G) ** i
    ebit = ebitda - dep
    pbt = ebit - INTEREST[i]
    pat = pbt * (1 - TAX)
    cum_pat += pat
    rows.append(dict(fy=FY[i], **{k: round(r[k], 1) for k in VERT}, total=total, ebitda=ebitda, pat=pat, cum_pat=cum_pat,
                     ebitda_m=ebitda / total, pat_m=pat / total))

for i, r in enumerate(rows):
    g_rev = (r["total"] / rows[i - 1]["total"] - 1) * 100 if i else None
    g_pat = (r["pat"] / rows[i - 1]["pat"] - 1) * 100 if i else None
    r["g_rev"], r["g_pat"] = g_rev, g_pat

print(f"{'FY':9}{'Cons':>8}{'Integ':>8}{'FM':>8}{'Train':>8}{'Total':>9}{'g%':>6}{'EBITDA':>8}{'EB%':>6}{'PAT':>8}{'PAT%':>6}{'gPAT':>6}{'cumPAT':>8}")
for r in rows:
    print(f"{r['fy']:9}{r['Consulting']:8.0f}{r['Integration']:8.0f}{r['Facility Maintenance']:8.0f}{r['Training']:8.0f}{r['total']:9.0f}"
          f"{(r['g_rev'] or 0):6.0f}{r['ebitda']:8.0f}{r['ebitda_m'] * 100:6.1f}{r['pat']:8.1f}{r['pat_m'] * 100:6.1f}{(r['g_pat'] or 0):6.0f}{r['cum_pat']:8.0f}")
ok = all(r["g_rev"] >= 30 and r["g_pat"] >= 30 for r in rows[1:])
print("30% check on top and bottom line every year:", ok)
pb = next((r["fy"] for r in rows if r["cum_pat"] >= EQUITY + LOAN), None)
print("payback of ₹150 lakh capital by cumulative PAT in:", pb)
with open(pathlib.Path(__file__).parent / "div_model.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["FY"] + list(VERT) + ["Total revenue", "EBITDA", "PAT", "Revenue growth %", "PAT growth %"])
    for r in rows:
        w.writerow([r["fy"]] + [round(r[k], 1) for k in VERT] + [round(r["total"], 1), round(r["ebitda"], 1), round(r["pat"], 1),
                   "" if r["g_rev"] is None else round(r["g_rev"], 1), "" if r["g_pat"] is None else round(r["g_pat"], 1)])

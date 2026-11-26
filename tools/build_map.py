"""Builds app/static/topografie/europe.json from Natural Earth (public domain).

Usage: python3 tools/build_map.py ne_50m_admin_0_map_subunits.geojson
Numbers follow the school worksheet 'Landen in Europa [1]' (Junior Einstein, groep 7/8).
"""
import json
import math
import sys

# worksheet number -> (Natural Earth unit codes, Dutch name)
COUNTRIES = {
    1: (["ISL"], "IJsland"), 2: (["NOR", "NJM"], "Noorwegen"), 3: (["SWE"], "Zweden"), 4: (["FIN", "ALD"], "Finland"),
    5: (["IRL"], "Ierland"), 6: (["NIR"], "Noord-Ierland"), 7: (["SCT"], "Schotland"), 8: (["ENG"], "Engeland"),
    9: (["WLS"], "Wales"), 10: (["DNK", "DNB"], "Denemarken"), 11: (["EST"], "Estland"), 12: (["LVA"], "Letland"),
    13: (["LTU"], "Litouwen"), 14: (["RUE", "RUK"], "Rusland"), 15: (["NLD"], "Nederland"),
    16: (["BFR", "BWR", "BCR"], "België"), 17: (["LUX"], "Luxemburg"), 18: (["DEU"], "Duitsland"), 19: (["POL"], "Polen"),
    20: (["BLR"], "Wit-Rusland"), 21: (["CZE"], "Tsjechië"), 22: (["FXX", "FXC"], "Frankrijk"), 23: (["CHE"], "Zwitserland"),
    24: (["AUT"], "Oostenrijk"), 25: (["SVK"], "Slowakije"), 26: (["UKR", "RUC"], "Oekraïne"),
    27: (["ITX", "ITY", "ITD", "ITP"], "Italië"), 28: (["SVN"], "Slovenië"), 29: (["HRV"], "Kroatië"), 30: (["HUN"], "Hongarije"),
    31: (["MDA"], "Moldavië"), 32: (["ROU"], "Roemenië"), 33: (["BIS", "BHF"], "Bosnië en Herzegovina"),
    34: (["SRS", "SRV"], "Servië"), 35: (["MNE"], "Montenegro"), 36: (["KOS"], "Kosovo"), 37: (["BGR"], "Bulgarije"),
    38: (["ALB"], "Albanië"), 39: (["MKD"], "Macedonië"), 40: (["GRC"], "Griekenland"), 41: (["TUR"], "Turkije"),
    42: (["PRX"], "Portugal"), 43: (["ESX", "ESI"], "Spanje"), 44: (["MLT"], "Malta"), 45: (["CYP", "CYN"], "Cyprus"),
}
LON0, LAT0 = math.radians(15), math.radians(52)       # Lambert azimuthal equal-area, like EU maps (EPSG:3035)
WIDTH = 1000


def proj(lon, lat):
    lam, phi = math.radians(lon), math.radians(lat)
    k = math.sqrt(2 / (1 + math.sin(LAT0) * math.sin(phi) + math.cos(LAT0) * math.cos(phi) * math.cos(lam - LON0)))
    x = k * math.cos(phi) * math.sin(lam - LON0)
    y = k * (math.cos(LAT0) * math.sin(phi) - math.sin(LAT0) * math.cos(phi) * math.cos(lam - LON0))
    return x, -y


def clip(ring, x0, y0, x1, y1):
    """Sutherland-Hodgman against a rectangle."""
    def cut(pts, inside, inter):
        out = []
        for i, p in enumerate(pts):
            q = pts[i - 1]
            if inside(p):
                if not inside(q):
                    out.append(inter(q, p))
                out.append(p)
            elif inside(q):
                out.append(inter(q, p))
        return out
    def ix(a, b, x):
        t = (x - a[0]) / (b[0] - a[0]); return (x, a[1] + t * (b[1] - a[1]))
    def iy(a, b, y):
        t = (y - a[1]) / (b[1] - a[1]); return (a[0] + t * (b[0] - a[0]), y)
    pts = ring
    for inside, inter in ((lambda p: p[0] >= x0, lambda a, b: ix(a, b, x0)), (lambda p: p[0] <= x1, lambda a, b: ix(a, b, x1)),
                          (lambda p: p[1] >= y0, lambda a, b: iy(a, b, y0)), (lambda p: p[1] <= y1, lambda a, b: iy(a, b, y1))):
        if not pts:
            break
        pts = cut(pts, inside, inter)
    return pts


def area(r):
    return abs(sum(r[i - 1][0] * r[i][1] - r[i][0] * r[i - 1][1] for i in range(len(r)))) / 2


def dp(pts, eps):
    """Douglas-Peucker simplification."""
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1e-9
    i, dmax = 0, 0
    for k in range(1, len(pts) - 1):
        d = abs(dy * pts[k][0] - dx * pts[k][1] + b[0] * a[1] - b[1] * a[0]) / n if n > 1e-9 else math.hypot(pts[k][0] - a[0], pts[k][1] - a[1])
        if d > dmax:
            i, dmax = k, d
    if dmax > eps:
        return dp(pts[:i + 1], eps)[:-1] + dp(pts[i:], eps)
    return [a, b]


def inside(pt, ring):
    x, y, c = pt[0], pt[1], False
    for i in range(len(ring)):
        (x1, y1), (x2, y2) = ring[i - 1], ring[i]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy or 1e-9)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def label_point(ring):
    """Point inside the polygon farthest from its edges (simple polylabel)."""
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    best, bd = None, -1
    for gx in range(41):
        for gy in range(41):
            p = (min(xs) + (max(xs) - min(xs)) * gx / 40, min(ys) + (max(ys) - min(ys)) * gy / 40)
            if inside(p, ring):
                d = min(seg_dist(p, ring[i - 1], ring[i]) for i in range(len(ring)))
                if d > bd:
                    best, bd = p, d
    return best or (sum(xs) / len(xs), sum(ys) / len(ys))


def main(path):
    feats = json.load(open(path))["features"]
    unit_to_num = {u: n for n, (units, _) in COUNTRIES.items() for u in units}
    # view: Iceland (west) to 46E, Nordkapp (north) to Cyprus (south)
    corners = [proj(-25, 66), proj(46, 50), proj(25, 71.5), proj(33, 34.3), proj(-10, 35.5), proj(44, 39)]
    x0, x1 = min(c[0] for c in corners), max(c[0] for c in corners)
    y0, y1 = min(c[1] for c in corners), max(c[1] for c in corners)
    pad = (x1 - x0) * 0.02
    x0, x1, y0, y1 = x0 - pad, x1 + pad, y0 - pad, y1 + pad
    s = WIDTH / (x1 - x0)
    H = round((y1 - y0) * s)
    countries = {n: [] for n in COUNTRIES}
    other = []
    for f in feats:
        p = f["properties"]
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        num = unit_to_num.get(p["SU_A3"])
        for poly in polys:
            ring = poly[0]
            if not any(-45 < lon < 75 and 25 < lat < 82 for lon, lat in ring):
                continue
            pr = [((x - x0) * s, (y - y0) * s) for x, y in (proj(lon, lat) for lon, lat in ring)]
            pr = clip(pr, 0, 0, WIDTH, H)
            if len(pr) < 3:
                continue
            pr = dp(pr + [pr[0]], 0.35)[:-1]
            if len(pr) < 3:
                continue
            a = area(pr)
            (countries[num] if num else other).append((a, pr))
    def d(rings):
        return "".join("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in r) + "Z" for r in rings)
    out = {"w": WIDTH, "h": H, "other": d([r for a, r in other if a > 3]), "countries": {}}
    for n, parts in countries.items():
        parts.sort(key=lambda t: -t[0])
        keep = [r for a, r in parts if a > 1.5] or [parts[0][1]]
        lx, ly = label_point(parts[0][1])
        xs = [x for r in keep for x, _ in r]
        ys = [y for r in keep for _, y in r]
        total = sum(a for a, r in parts)
        out["countries"][n] = {"name": COUNTRIES[n][1], "d": d(keep), "label": [round(lx, 1), round(ly, 1)],
                               "dot": total < 60,
                               "box": [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)]}
    json.dump(out, open("app/static/topografie/europe.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print("map", WIDTH, "x", H, "size", len(json.dumps(out)) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])

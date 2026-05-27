def choose_move(observation):
    g = observation if isinstance(observation, dict) else {}
    iv = lambda x, d=0: x if isinstance(x, int) else (int(x) if isinstance(x, float) or (isinstance(x, str) and x.lstrip("-").isdigit()) else d)
    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return iv(v[0]), iv(v[1])
        if isinstance(v, dict):
            for k in ("position", "pos", "loc", "location"):
                if k in v:
                    return pos(v[k])
        return 0, 0
    def items(v):
        return v if isinstance(v, list) else ([] if v is None else [v])
    w = iv(g.get("grid_width", g.get("width", 0)))
    h = iv(g.get("grid_height", g.get("height", 0)))
    sx, sy = pos(g.get("self_position", g.get("self", (0, 0))))
    ox, oy = pos(g.get("opponent_position", g.get("opponent", (0, 0))))
    obs = {pos(x) for x in items(g.get("obstacles", []))}
    pts = []
    for k in ("resources", "targets", "control_points", "points", "goals"):
        for v in items(g.get(k, [])):
            pts.append(pos(v.get("position", v)) if isinstance(v, dict) else pos(v))
    if not pts:
        pts = [(ox, oy)]
    def best_target():
        b = None
        for x, y in pts:
            d = abs(x - sx) + abs(y - sy)
            e = abs(x - ox) + abs(y - oy)
            s = d * 2 - e
            if b is None or s < b[0] or (s == b[0] and d < b[1]):
                b = (s, d, x, y)
        return b[2], b[3]
    tx, ty = best_target()
    cands = [(0, 0)]
    cands += [(1, 0), (-1, 0)] if abs(tx - sx) >= abs(ty - sy) else [(0, 1), (0, -1)]
    cands += [(0, 1), (0, -1)] if abs(tx - sx) >= abs(ty - sy) else [(1, 0), (-1, 0)]
    cands += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    seen, out = set(), [0, 0]
    best = None
    for dx, dy in cands:
        if (dx, dy) in seen:
            continue
        seen.add((dx, dy))
        nx, ny = sx + dx, sy + dy
        if w and not (0 <= nx < w) or h and not (0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        danger = abs(nx - ox) + abs(ny - oy)
        score = d * 3 - danger
        if best is None or score < best[0] or (score == best[0] and (dx, dy) < tuple(out)):
            best = (score, dx, dy)
            out = [dx, dy]
    return out

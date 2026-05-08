def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", sp)
    def xy(p, d=(0, 0)):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return (int(p[0]), int(p[1]))
        if isinstance(p, dict):
            q = p.get("position", p.get("pos", p.get("location", d)))
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (int(q[0]), int(q[1]))
        return d
    sx, sy = xy(sp, (0, 0))
    ox, oy = xy(op, (sx, sy))
    obs = set()
    for o in observation.get("obstacles", []) or []:
        xo, yo = xy(o, None) if o is not None else (None, None)
        if xo is not None and 0 <= xo < w and 0 <= yo < h:
            obs.add((xo, yo))
    resources = []
    for r in observation.get("resources", []) or []:
        xr, yr = xy(r, None) if r is not None else (None, None)
        if xr is not None and 0 <= xr < w and 0 <= yr < h and (xr, yr) not in obs:
            resources.append((xr, yr))
    if not resources:
        return [0, 0]
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    best = None
    best_key = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (od - sd, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    bestm = None
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            nd = abs(tx - nx) + abs(ty - ny)
            if bestd is None or nd < bestd or (nd == bestd and (dx, dy) < bestm):
                bestd = nd
                bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]
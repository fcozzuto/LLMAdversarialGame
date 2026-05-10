def choose_move(observation):
    def to_xy(p):
        if p is None:
            return None
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                return int(p["position"][0]), int(p["position"][1])
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return None

    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = to_xy(observation.get("self_position")) or (0, 0)
    ox, oy = to_xy(observation.get("opponent_position")) or (0, 0)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        q = to_xy(p)
        if q is not None:
            blocked.add(q)

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        q = to_xy(r)
        if q is not None:
            res.append(q)

    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not res:
        tx, ty = ox, oy
        best = None
        bestd = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not clamp_in(nx, ny):
                continue
            d = max(abs(nx - tx), abs(ny - ty))
            if best is None or d < bestd:
                best = (dx, dy); bestd = d
        return list(best) if best is not None else [0, 0]

    def dist(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    # Choose resource that is closer than opponent (otherwise closest to self), deterministic tie-break.
    best = None
    bestk = None
    for rx, ry in res:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        k = (0 if ds <= do else 1, ds, rx, ry)
        if best is None or k < bestk:
            bestk = k
            best = (rx, ry)

    tx, ty = best
    best_move = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        s_new = dist(nx, ny, tx, ty)
        o_new = dist(nx, ny, ox, oy)
        score = (s_new, -o_new, dx, dy)
        if best_move is None or score < best_score:
            best_move = (dx, dy); best_score = score

    return [best_move[0], best_move[1]] if best_move is not None else [0, 0]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    def get_xy(key, fallback):
        v = observation.get(key)
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            try:
                return int(v[0]), int(v[1])
            except:
                pass
        if isinstance(fallback, (list, tuple)) and len(fallback) >= 2:
            return int(fallback[0]), int(fallback[1])
        return 0, 0

    sx, sy = get_xy("self_position", [0, 0])
    ox, oy = get_xy("opponent_position", [w - 1, h - 1])

    obstacles_raw = observation.get("obstacles", None)
    obs = set()
    if obstacles_raw:
        for p in obstacles_raw:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    obs.add((int(p[0]), int(p[1])))
                except:
                    pass

    oppT = set()
    oppT_raw = observation.get("opponent_territory", None)
    if oppT_raw:
        for p in oppT_raw:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    oppT.add((int(p[0]), int(p[1])))
                except:
                    pass

    res_raw = observation.get("resources", None)
    resources = []
    if res_raw:
        for p in res_raw:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    resources.append((int(p[0]), int(p[1])))
                except:
                    pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    bestv = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        d_op = dist(nx, ny, ox, oy)
        d_res = 0
        if resources:
            dmin = None
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
            d_res = dmin if dmin is not None else 0
        penalty = 0
        if (nx, ny) in oppT:
            penalty = 50

        v = d_op + (0.35 * d_res) + penalty

        if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or (0, 0)
    o = observation.get("opponent_position") or s
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = observation.get("obstacles") or []
    blocked = set((int(p[0]), int(p[1])) for p in obs)

    res = observation.get("resources") or []
    resources = [(int(p[0]), int(p[1])) for p in res] if isinstance(res, (list, tuple)) else []
    myterrit = observation.get("self_territory") or []
    myset = set((int(p[0]), int(p[1])) for p in myterrit) if isinstance(myterrit, (list, tuple)) else set()

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_val = -10**18

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_opp = manh((nx, ny), (ox, oy))
        d_best_res = 10**9
        for r in resources:
            d = manh((nx, ny), r)
            if d < d_best_res:
                d_best_res = d
        if not resources:
            d_best_res = 0
        val = 0
        val += 1000 if (nx, ny) in myset else 0
        if resources:
            val += 2000 - 10 * d_best_res
        val += 5 * d_opp
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
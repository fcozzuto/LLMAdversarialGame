def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res_set = set((r[0], r[1]) for r in resources if r is not None)

    best = None
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        if (nx, ny) in res_set:
            val = 10**6
        else:
            val = -cheb(nx, ny, ox, oy)  # keep away a bit
            # maximize advantage over opponent for best reachable resource
            sd = 10**9
            od = 10**9
            for rx, ry in res_set:
                if (rx, ry) in blocked:
                    continue
                d1 = cheb(nx, ny, rx, ry)
                d2 = cheb(ox, oy, rx, ry)
                if d1 < sd:
                    sd = d1
                    od = d2
                elif d1 == sd and d2 < od:
                    od = d2
            if sd != 10**9:
                val += (od - sd) * 100 - sd
        key = (val, dx, dy)
        if best is None or key > (best_val, best[0], best[1]):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
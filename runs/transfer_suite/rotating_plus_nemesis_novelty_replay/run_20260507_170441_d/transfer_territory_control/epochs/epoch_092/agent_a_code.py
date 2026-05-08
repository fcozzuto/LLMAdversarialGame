def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    res = observation.get("resources") or []
    resources = []
    for p in res:
        try:
            resources.append((int(p[0]), int(p[1]), int(p[2]) if len(p) > 2 else 1))
        except:
            try:
                resources.append((int(p[0]), int(p[1]), 1))
            except:
                pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mindist_to_set(x, y, S):
        if not S:
            return None
        d2 = None
        for a, b in S:
            dd = (x - a) * (x - a) + (y - b) * (y - b)
            if d2 is None or dd < d2:
                d2 = dd
        return d2

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dxdy = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        val = 0
        if (nx, ny) in opp_t:
            val -= 10**9
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val += d_opp // 2
        d_unc = mindist_to_set(nx, ny, unclaimed)
        if d_unc is not None:
            val += max(0, 200000 - d_unc)
        else:
            d_unc2 = None
            for a, b, _ in resources[:10]:
                dd = (nx - a) * (nx - a) + (ny - b) * (ny - b)
                if d_unc2 is None or dd < d_unc2:
                    d_unc2 = dd
            if d_unc2 is not None:
                val += max(0, 150000 - d_unc2)
        if dx == 0 and dy == 0:
            val -= 1
        if val > best_val:
            best_val = val
            best_dxdy = (dx, dy)
    return [int(best_dxdy[0]), int(best_dxdy[1])]
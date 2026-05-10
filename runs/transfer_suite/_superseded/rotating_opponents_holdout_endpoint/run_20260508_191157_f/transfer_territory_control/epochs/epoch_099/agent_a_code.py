def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    unC_list = observation.get("unclaimed_cells") or []
    unC = set((int(x), int(y)) for x, y in unC_list)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    unC_list2 = list(unC)
    def min_dist_to_unclaimed(x, y):
        if not unC_list2:
            return 999
        md = 10**9
        for ux, uy in unC_list2:
            d = abs(x - ux) + abs(y - uy)
            if d < md:
                md = d
        return md

    def adj_to_self(x, y):
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in selfT:
                return True
        return False

    best = (0, 0)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_center = abs(nx - cx) + abs(ny - cy)
        d_un = min_dist_to_unclaimed(nx, ny)

        if (nx, ny) in selfT:
            s = 2500 - 25 * d_center - 2 * d_opp
            if adj_to_self(nx, ny):
                s += 120
        elif (nx, ny) in unC:
            s = 6000 - 80 * d_un - 30 * d_center - 1.5 * d_opp
            if adj_to_self(nx, ny):
                s += 1800
            s -= 0.5 * max(0, d_opp - 2)
        elif (nx, ny) in oppT:
            s = -90000 + 900 * (1 if adj_to_self(nx, ny) else 0) - 40 * d_un - 10 * d_opp
        else:
            s = -1000 - 20 * d_un - 20 * d_center

        if s > best_s or (s == best_s and (dx, dy) < best):
            best_s = s
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
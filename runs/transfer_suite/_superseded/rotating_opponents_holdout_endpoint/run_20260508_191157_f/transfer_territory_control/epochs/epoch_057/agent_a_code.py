def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def to_set(val):
        s = set()
        for p in val or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    unclaimed = to_set(observation.get("unclaimed_cells"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    unclaimed_list = list(unclaimed)
    if unclaimed_list:
        nearest_unclaimed = min(unclaimed_list, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    else:
        nearest_unclaimed = None

    opp_front = []
    if selfT and oppT:
        for (x, y) in selfT:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in oppT:
                    opp_front.append((nx, ny))
    opp_front = opp_front[:]

    best = None
    best_sc = -10**18
    for dx, dy, nx, ny in candidates:
        sc = 0
        if (nx, ny) in unclaimed:
            sc += 7
        if (nx, ny) in selfT:
            sc += 2
        if (nx, ny) in oppT:
            sc += 5

        if nearest_unclaimed is not None:
            d = abs(nx - nearest_unclaimed[0]) + abs(ny - nearest_unclaimed[1])
            sc += 3 - min(3, d)  # prefer reducing distance early
        elif opp_front:
            tf = min(opp_front, key=lambda c: abs(c[0] - nx) + abs(c[1] - ny))
            d = abs(nx - tf[0]) + abs(ny - tf[1])
            sc += 4 - min(4, d)
        else:
            sc += -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.01

        # slight bias to avoid wasting moves when close to borders/territory change spots
        if (nx, ny) in oppT:
            sc += 0.1

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
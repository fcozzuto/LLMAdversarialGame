def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    px, py = observation.get("opponent_position") or [w - 1, h - 1]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if x is not None and y is not None:
                obstacles.add((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed_set = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def score_at(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**9
        is_opp = (x, y) in opp_set
        is_un = (x, y) in unclaimed_set
        is_self = (x, y) in self_set
        base = (7 if is_opp else 4 if is_un else 2 if is_self else 0)

        # Prefer expansion: adjacent unclaimed.
        adj_un = 0
        adj_opp = 0
        adj_obs = 0
        for dx, dy in dirs8:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                adj_obs += 1
            elif (nx, ny) in unclaimed_set:
                adj_un += 1
            elif (nx, ny) in opp_set:
                adj_opp += 1

        # Cut off: move slightly away from opponent to avoid getting front-stacked.
        dist_c = abs(x - cx) + abs(y - cy)
        dist_p = abs(x - px) + abs(y - py)
        # Maximize dist_p, minimize dist_c slightly to keep center control.
        center_term = -0.05 * dist_c
        opp_term = 0.08 * dist_p

        # Risk term: avoid being adjacent to many opponent cells unless capturing.
        risk = 0.3 * adj_opp - 0.05 * adj_un + 0.25 * adj_obs
        if is_opp:
            risk -= 0.6  # encourage flipping when stepping onto opponent territory

        return base + 0.6 * adj_un + center_term + opp_term - risk

    best = (-(10**18), 0, 0)
    for dx, dy in dirs8:
        x, y = sx + dx, sy + dy
        sc = score_at(x, y)
        if sc > best[0]:
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]
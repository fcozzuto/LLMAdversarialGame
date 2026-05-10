def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in self_role) or ("pursuer" in opp_role and ("evader" in self_role))
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    neigh = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def free_count(x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if legal(nx, ny):
                c += 1
        return c

    def score(nx, ny):
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if self_is_evader:
            s = -d2
            s += 3.0 * free_count(nx, ny)
            return s
        # Pursuer: minimize distance while avoiding dead-ends and preferring "walling" via mobility reduction near opponent.
        s = d2
        s -= 0.35 * free_count(nx, ny)  # fewer exits is fine if it helps trap; but keep small
        # If we can cut off opponent by aligning to reduce its options near its current position, reward.
        opp_free = free_count(ox, oy)
        opp_free_after = 0
        for dx, dy in neigh:
            tx, ty = ox + dx, oy + dy
            if not legal(tx, ty):
                continue
            # If our move would occupy a candidate next cell, heavily penalize for evader options (capture radius 0: still helps).
            if tx == nx and ty == ny:
                opp_free_after += 2
            else:
                opp_free_after += 1
        s += -0.15 * (opp_free_after - opp_free)  # reward when opponent gets fewer viable moves
        return s

    best = None
    best_dxdy = [0, 0]
    # Deterministic tie-break: fixed move order already; compare using key (primary score, then distance to center, then lexicographic).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = score(nx, ny)
        center_bias = (nx - (w - 1) / 2.0) * (nx - (w - 1) / 2.0) + (ny - (h - 1) / 2.0) * (ny - (h - 1) / 2.0)
        key = (v, center_bias, dx, dy)
        if best is None or key < best:
            best = key
            best_dxdy = [dx, dy]
    return [int(best_dxdy[0]), int(best_dxdy[1])]
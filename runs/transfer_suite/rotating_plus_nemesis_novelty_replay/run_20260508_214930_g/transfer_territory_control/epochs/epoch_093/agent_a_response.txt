def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Frontier targets: unclaimed next to our territory.
    frontier = set()
    for (x, y) in self_t:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                frontier.add((nx, ny))
    candidates = frontier if frontier else unclaimed

    # Pick deterministic best target.
    if not candidates:
        return [0, 0]
    best_t = None
    best_k = None
    for tx, ty in candidates:
        # Prefer targets that help edge pressure (same row/col) and reduce distance to opponent.
        edge_bonus = 6 if (tx == 0 or ty == 0 or tx == w - 1 or ty == h - 1) else 0
        near_opp = -(abs(tx - ox) + abs(ty - oy))
        k = (abs(tx - sx) + abs(ty - sy), -edge_bonus, -near_opp, ty, tx)
        if best_k is None or k < best_k:
            best_k = k
            best_t = (tx, ty)
    tx, ty = best_t

    # Evaluate immediate moves with a strong preference toward chosen target.
    best_move = (0, 0)
    best_s = -10**18
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny):
            continue
        # Move quality: toward target; avoid opponent territory unless it grants capture value.
        dist_now = abs(sx - tx) + abs(sy - ty)
        dist_next = abs(nx - tx) + abs(ny - ty)
        toward = (dist_now - dist_next)
        opp_cap = 1200 if (nx, ny) in opp_t else 0
        own_hold = 5 if (nx, ny) in self_t else 0
        uncl = 60 if (nx, ny) in unclaimed else 0
        edge = 10 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        avoid_corner_trap = -8 if (nx, ny) in opp_t else 0
        # Also slightly reduce distance to opponent to counter edge-claim.
        prox = -(abs(nx - ox) + abs(ny - oy)) + (abs(sx - ox) + abs(sy - oy)) * 0.05
        s = toward * 30 + opp_cap + uncl + own_hold + edge + avoid_corner_trap + prox
        if s > best_s:
            best_s = s
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]
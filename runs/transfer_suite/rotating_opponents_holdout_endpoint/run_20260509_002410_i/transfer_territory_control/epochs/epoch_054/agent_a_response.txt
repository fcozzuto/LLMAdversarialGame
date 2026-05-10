def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_val = -10**18
    best = [0, 0]

    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer moving toward center and expanding territory.
        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_opp = abs(nx - ox) + abs(ny - oy)

        val = 0.0
        if (nx, ny) in self_t:
            val += 0.2
        elif (nx, ny) in unclaimed:
            val += 1.4
        elif (nx, ny) in opp_t:
            # Flipping is enabled on entry; treat capturing as valuable.
            val += 2.2

        # Strategic pressure: move closer to opponent when it doesn't cost center progress too much.
        val += 0.05 * (dist_opp * -1)
        val += 0.12 * (dist_center * -1)

        # Mild obstacle aversion
        adj_obs = 0
        for ax, ay in dirs[:-1]:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obstacles:
                adj_obs += 1
        val -= 0.08 * adj_obs

        # Deterministic tie-breaker: prefer smaller dx, then smaller dy, then stay
        key = (val, -abs(dx) - abs(dy), - (dx * 3 + dy))
        cur_best_key = (best_val, -abs(best[0]) - abs(best[1]), - (best[0] * 3 + best[1]))
        if key > cur_best_key:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]
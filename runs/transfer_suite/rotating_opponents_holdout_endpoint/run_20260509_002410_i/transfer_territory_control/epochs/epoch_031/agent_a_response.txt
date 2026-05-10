def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    # Prefer safe expansion to center, but strongly counter-claim adjacent opponent cells.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        d_op = man(nx, ny, ox, oy)
        d_center = man(nx, ny, cx, cy)

        if (nx, ny) in opp_t:
            score += 50000.0 - 25.0 * d_op
        elif (nx, ny) in unclaimed:
            score += 6000.0 - 3.0 * d_op - 8.0 * d_center
        elif (nx, ny) in self_t:
            score += 800.0 - 4.0 * d_center
        else:
            score += 200.0 - 6.0 * d_center

        # Small bias to keep moving; prefer higher progress toward center unless countering opponent.
        score += 2.0 * (man(sx, sy, cx, cy) - d_center)

        # Avoid stepping onto cells adjacent to obstacles too often (micro safety).
        adj_obs = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if inside(ax, ay) and (ax, ay) in obstacles:
                adj_obs += 1
        score -= 5.0 * adj_obs

        # Deterministic tie-break: fixed iteration order already, but keep numeric tie stable.
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
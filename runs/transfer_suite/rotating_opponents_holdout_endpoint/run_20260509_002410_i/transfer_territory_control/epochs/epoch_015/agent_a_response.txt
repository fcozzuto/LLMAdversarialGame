def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if (nx, ny) == (sx, sy) and (sx + dx, sy + dy) in obstacles:
            pass

        score = 0.0
        if (nx, ny) in opp_t:
            score += 25.0
        if (nx, ny) in unclaimed:
            score += 8.0
        if (nx, ny) in self_t:
            score += 2.0

        # Progress: chase opponent and also reduce their control/edge distance.
        score += -abs(nx - ox) - abs(ny - oy)

        # Encourage pushing toward center to meet and capture territory.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += -0.15 * (abs(nx - cx) + abs(ny - cy))

        # If adjacent to opponent territory, prefer it.
        adj_opp = False
        for ex, ey in dirs[1:]:
            ax, ay = nx + ex, ny + ey
            if inside(ax, ay) and (ax, ay) in opp_t:
                adj_opp = True
                break
        if adj_opp:
            score += 6.0

        # Small deterministic tie-break: prefer movement over staying.
        if dx == 0 and dy == 0:
            score -= 0.2

        key = (-score, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [int(best[1]), int(best[2])]
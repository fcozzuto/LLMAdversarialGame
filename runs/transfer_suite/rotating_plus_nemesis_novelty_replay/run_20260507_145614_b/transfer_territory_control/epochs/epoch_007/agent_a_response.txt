def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            self_t.add((p[0], p[1]))

    opp_t = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            opp_t.add((p[0], p[1]))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            unclaimed.add((p[0], p[1]))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_t:
            base = 120.0
        elif (nx, ny) in unclaimed:
            base = 18.0
        elif (nx, ny) in self_t:
            base = 3.0
        else:
            base = 6.0

        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)

        # Prefer central expansion while also threatening opponent territory
        score = base + (-0.9 * d_center) + (-0.25 * d_opp)

        # Slightly prefer moves that reduce distance to any opponent territory cell if visible
        # (deterministic, no extra search)
        if observation.get("opponent_territory_count", 0) > 0:
            d_self_to_opp = abs(sx - ox) + abs(sy - oy)
            score += 1.5 if d_opp < d_self_to_opp else 0.0

        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]
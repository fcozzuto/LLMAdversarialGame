def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def corner_bias(x, y):
        # keep moving toward nearest outer edge to reduce wandering
        dx0 = x
        dx1 = (gw - 1) - x
        dy0 = y
        dy1 = (gh - 1) - y
        return min(dx0, dx1) + min(dy0, dy1)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # If staying, allow only if no better moves
        local = 0
        # Prefer resources that we can reach sooner than opponent
        for rx, ry in res:
            myd = manhattan(nx, ny, rx, ry)
            if myd == 0:
                return [dx, dy]
            opd = manhattan(ox, oy, rx, ry)

            # Tradeoff:
            # - prioritize being earlier
            # - slight preference for closer resources
            # - penalize if opponent is much closer and likely to contest
            contest_pen = 0
            if opd <= myd:
                contest_pen = (myd - opd + 2) * 5
            # also bias toward blocking lines near opponent (resource_denier)
            opp_line = (manhattan(nx, ny, ox, oy) - manhattan(ox, oy, rx, ry))
            local_score = (opd - myd) * 12 - myd * 2 - contest_pen + (0.5 if opp_line < 0 else 0)
            if (rx, ry) in obs:
                local_score -= 1000
            local += local_score / (1 + myd)

        # small tie-break toward edge direction and away from immediate proximity to opponent
        local += -manhattan(nx, ny, ox, oy) * 0.15 + corner_bias(nx, ny) * 0.01

        if local > best_score:
            best_score = local
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
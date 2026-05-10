def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    scores = observation.get("scores") or {}
    gap = 0
    if isinstance(scores, dict):
        gap = scores.get(observation.get("self_name"), 0) - scores.get(observation.get("opponent_name"), 0)
    behind = gap < -1

    # Build opponent frontier: unclaimed or our-avoidable cells that are adjacent to opponent territory.
    frontier = set()
    for (px, py) in opp_terr:
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed or (nx, ny) in self_terr:
                    frontier.add((nx, ny))

    # Deterministic tie-break: prefer diagonal toward frontier, then toward center, then stay.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = [0, 0]
    best_val = -10**18
    best_primary = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary: immediate gain on contact/entry.
        primary = 0
        if (nx, ny) in opp_terr:
            primary += 120  # flipping opponent-owned cell
        elif (nx, ny) in unclaimed:
            primary += 25
        elif (nx, ny) in self_terr:
            primary += 6
        else:
            primary += 2

        # Secondary: chase frontier when behind; otherwise take opportunities that increase distance from opponent.
        secondary = 0
        if frontier:
            d_front = min(dist(nx, ny, fx, fy) for (fx, fy) in frontier)
            secondary += (60 - 10 * d_front) if behind else (35 - 6 * d_front)
        else:
            d_opp = dist(nx, ny, ox, oy)
            secondary += (d_opp * 2) if not behind else (35 - d_opp)

        # Obstacle/edge discouragement: slightly prefer keeping mobility.
        mobility = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if inside(tx, ty) and (tx, ty) not in obstacles:
                mobility += 1
        tertiary = mobility * 0.5

        val = primary * 10 + secondary + tertiary
        # Deterministic tie-break
        tie = 0
        if dx != 0 or dy != 0:
            tie = -dist(nx, ny, cx, cy)
        else:
            tie = -200  # prefer moving over staying when equal

        if val > best_val or (val == best_val and tie > best_primary):
            best_val = val
            best_primary = tie
            best_move = [dx, dy]

    return best_move if isinstance(best_move, list) else [0, 0]
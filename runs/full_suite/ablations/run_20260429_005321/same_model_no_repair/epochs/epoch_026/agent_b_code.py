def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Focus on resources that opponent tends to reach early (interception)
    opp_sorted = sorted(resources, key=lambda r: man(ox, oy, r[0], r[1]))
    k = 4 if len(opp_sorted) >= 4 else len(opp_sorted)
    contested = opp_sorted[:k]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, - -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue

        self_min = 10**9
        score = 0.0

        for rx, ry in contested:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            self_min = ds if ds < self_min else self_min
            # Only meaningfully contest resources where opponent is not far behind us
            if do <= ds + 2:
                score += (do - ds) * 3.0  # positive if we are closer
            # Encourage reducing our distance to these contested resources
            score += -ds * 0.15

        # Also reduce distance to the nearest resource overall
        overall_min = min(man(nx, ny, r[0], r[1]) for r in resources)
        score += -overall_min * 0.35

        # Slight preference for advancing toward contested area (avoid drifting)
        nearest_opp = min(man(nx, ny, r[0], r[1]) for r in contested) if contested else 0
        score += -nearest_opp * 0.05

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move
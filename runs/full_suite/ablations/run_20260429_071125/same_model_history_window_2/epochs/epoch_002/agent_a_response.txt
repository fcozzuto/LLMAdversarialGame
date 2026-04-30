def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    # Heuristic: pick the next step that maximizes "resource advantage"
    # advantage favors being closer than opponent, and being able to arrive soon.
    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        cur_best = None
        for rx, ry in resources:
            our_d = md((nx, ny), (rx, ry))
            opp_d = md((ox, oy), (rx, ry))

            # If opponent is also close, we want to be even closer; otherwise just rush.
            # Add small term to discourage giving opponent an easy "next-closest" position.
            adv = (opp_d - our_d) * 10 - our_d
            # Encourage moving toward clusters of resources (more progress, less wandering)
            # via distance to nearest resource from candidate.
            # (Computed cheaply as min dist from this candidate)
            # We approximate cluster effect by subtracting our_d to chosen resource only.
            # Tie-break with distance to opponent: don't step into opponent threat when equal.
            key = (adv, -md((nx, ny), (ox, oy)), -our_d, rx, ry)
            if cur_best is None or key > cur_best:
                cur_best = key

        if cur_best is None:
            continue
        if best is None or cur_best > best:
            best = cur_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
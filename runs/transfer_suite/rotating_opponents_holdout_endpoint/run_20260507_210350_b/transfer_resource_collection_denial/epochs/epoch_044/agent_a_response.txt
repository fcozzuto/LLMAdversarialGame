def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose best move by maximizing our post-move lead over the opponent for the best available resource.
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # For this hypothetical position, compute best resource lead we can achieve.
        local_best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            lead = opp_d - self_d  # positive means we are closer
            # Prefer larger lead, then smaller self distance, then deterministic coordinates.
            key = (lead, -self_d, -rx, -ry)
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue

        # Slight preference for moves that reduce our distance to the overall closest resource.
        closest_self = min(abs(int(r[0]) - nx) + abs(int(r[1]) - ny) for r in resources)
        move_key = (local_best[0], local_best[1], -closest_self, dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_key is not None else [0, 0]
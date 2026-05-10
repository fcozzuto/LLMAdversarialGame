def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Candidate moves, prefer progress (deterministic tie-break by index)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, 10**9, 0, 0)  # (neg_adv, myd, rx, ry)
    best_move = (0, 0)

    # Choose move by best immediate improvement for the "most contestable" resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate resources: want to maximize (opponent_dist - my_dist), then minimize my_dist.
        # Secondary tie-break by stable value from resource coordinates.
        local_best = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            key = (-adv, myd, (rx * 31 + ry) % 1000)
            if local_best is None or key < local_best:
                local_best = key
        # local_best must exist since resources non-empty
        neg_adv, myd, tie = local_best
        global_key = (neg_adv, myd, tie, (dx * 3 + dy) % 10)
        if global_key < best:
            best = global_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
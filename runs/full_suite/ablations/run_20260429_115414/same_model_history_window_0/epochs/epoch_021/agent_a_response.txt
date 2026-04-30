def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    sx, sy = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    if not resources:
        return [0, 0]

    best = None
    # Choose resource with maximum distance advantage vs opponent; tiebreak by our closer distance.
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = d((sx, sy), (rx, ry))
        do = d((ox, oy), (rx, ry))
        adv = do - ds
        key = (adv, -ds, -abs((rx + ry) - (sx + sy)))
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ds_new = d((nx, ny), (tx, ty))
        # Prefer reducing distance; small preference to keep away from opponent to reduce contention.
        opp_dist = d((nx, ny), (ox, oy))
        score = (-ds_new, opp_dist, dx == 0 and dy == 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
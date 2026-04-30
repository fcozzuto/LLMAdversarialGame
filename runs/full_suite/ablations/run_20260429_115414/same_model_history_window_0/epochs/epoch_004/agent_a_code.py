def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    # Deterministic move ordering (prefers diagonals, then straight, then stay)
    deltas = [
        (-1, -1), (0, -1), (1, -1),
        (-1,  0), (0,  0), (1,  0),
        (-1,  1), (0,  1), (1,  1),
    ]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick best target: prefer closest resource; if opponent is closer, take next best deterministically.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist2((sx, sy), (rx, ry))
        od = dist2((ox, oy), (rx, ry))
        # Penalize targets where opponent is much closer
        score = sd - (0.9 * od)
        if best is None or score < best[0] or (score == best[0] and (rx, ry) < best[1]):
            best = (score, (rx, ry))
    if best is None:
        return [0, 0]

    tx, ty = best[1]

    # Choose one-step move that minimizes distance to target while avoiding obstacles and bounds.
    best_move = (0, 0)
    best_d = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist2((nx, ny), (tx, ty))
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)

    # If we somehow couldn't move (all blocked), stay.
    if best_d is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
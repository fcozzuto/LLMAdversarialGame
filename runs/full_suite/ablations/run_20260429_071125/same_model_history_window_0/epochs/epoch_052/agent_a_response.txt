def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy)

    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    # Strategic change: go for resources where we are relatively better than opponent.
    # If none exist (all unreachable/empty), intercept by moving to reduce distance to opponent.
    best = None
    best_val = None
    for rx, ry in resources:
        d_s = dist((sx, sy), (rx, ry))
        d_o = dist((ox, oy), (rx, ry))
        # Prefer closer to us and farther from opponent (contest avoidance).
        val = (d_s * 1.0) - (d_o * 0.8)
        if best_val is None or val < best_val or (val == best_val and (rx, ry) < best):
            best_val = val
            best = (rx, ry)

    target = best
    if target is None:
        # No resources: move to opponent to potentially deny.
        tx, ty = ox, oy
    else:
        tx, ty = target

    # Choose move that best reduces distance to target; slight repulsion from opponent.
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_t = dist((nx, ny), (tx, ty))
        d_op = dist((nx, ny), (ox, oy))
        score = d_t - 0.15 * d_op
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
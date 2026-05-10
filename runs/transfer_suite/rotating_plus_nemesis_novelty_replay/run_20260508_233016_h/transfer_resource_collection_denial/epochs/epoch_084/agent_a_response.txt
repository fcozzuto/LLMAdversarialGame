def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {tuple(p) for p in obs_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    if not resources:
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        # Prefer targets where we are not slower; break ties by closer to us
        # Key ordering: higher slack (op - me), then smaller my_d, then lex by coords
        slack = op_d - my_d
        key = (-slack, my_d, rx, ry) if slack >= 0 else (0, my_d + (my_d - op_d) * 2, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    op_d0 = dist(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        my_next_d = dist(nx, ny, tx, ty)
        slack_next = op_d0 - my_next_d
        # Prefer maximizing slack, then minimizing distance, then deterministic tie-break by delta order
        score = (-slack_next, my_next_d, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
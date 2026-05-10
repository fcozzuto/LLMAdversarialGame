def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick a target resource with best "secure margin" (how much earlier we arrive than opponent).
    best = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        margin = op_d - my_d  # positive means we are earlier
        # If we can't secure (margin <= 0), still pick the one where we are "least behind" to contest.
        key = (-1 if margin > 0 else 1, -margin, my_d, op_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), my_d, op_d)
    (tx, ty) = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_my = dist(sx, sy, tx, ty)
    cur_op = dist(ox, oy, tx, ty)

    # Move one step to reduce distance to target; if tied, choose move that maximizes opponent distance to target.
    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d2 = dist(nx, ny, tx, ty)
        op_d2 = cur_op  # opponent position doesn't change on our move
        # Primary: get closer; Secondary: avoid wandering; Tertiary: keep opponent effectively less threatening by choosing path that improves our arrival.
        key = (my_d2, abs(my_d2 - cur_my), -op_d2, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move
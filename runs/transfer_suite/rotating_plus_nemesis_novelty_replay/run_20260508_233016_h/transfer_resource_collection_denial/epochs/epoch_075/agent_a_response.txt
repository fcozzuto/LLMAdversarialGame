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
        return dx if dx > dy else dy  # Chebyshev (king distance)

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        if my_d < op_d:
            key = (0, my_d, -op_d, rx, ry)  # secure: closer for us, farther for opp
        else:
            key = (1, -(op_d - my_d), my_d, -op_d, rx, ry)  # denial: maximize opp lag, then get closer
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    mode_secure = dist(sx, sy, tx, ty) < dist(ox, oy, tx, ty)
    best_mv = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_next = dist(nx, ny, tx, ty)
        op_next = dist(ox, oy, tx, ty)  # opponent static for decision; deterministic local heuristic
        gap = op_next - my_next

        if mode_secure:
            val = (my_next, -gap, dx == 0 and dy == 0)  # minimize our distance, keep gap
        else:
            val = (-gap, my_next, dx == 0 and dy == 0)  # maximize our denial gap, then get closer

        if best_val is None or val < best_val:
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]
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
        return dx if dx > dy else dy  # Chebyshev

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        # Prefer resources we can secure (reach strictly earlier), else choose a resource
        # that maximizes opponent delay while still moving us toward something useful.
        if my_d < op_d:
            key = (0, my_d, op_d, rx, ry)
        else:
            key = (1, -(op_d - my_d), my_d, op_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Greedy one-step with obstacle avoidance and opponent-aware tie-break.
    my_best = None
    my_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_to = dist(nx, ny, tx, ty)
        op_to = dist(ox, oy, tx, ty)
        # If opponent is likely to arrive first, add a small "denial" pressure: move away from positions
        # that would make us drop off too far relative to opponent.
        denial = (my_to - (op_to if op_to <= my_to else op_to + 1))
        key = (my_to, denial, abs((nx - ox)) + abs((ny - oy)), dx, dy)
        if my_key is None or key < my_key:
            my_key = key
            my_best = (dx, dy)

    if my_best is None:
        # All moves blocked; stay.
        return [0, 0]
    return [int(my_best[0]), int(my_best[1])]
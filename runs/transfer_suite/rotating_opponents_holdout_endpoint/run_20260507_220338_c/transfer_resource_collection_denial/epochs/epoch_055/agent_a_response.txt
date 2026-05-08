def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    my_best = min((man(sx, sy, rx, ry), (rx, ry)) for rx, ry in resources)
    op_best = min((man(ox, oy, rx, ry), (rx, ry)) for rx, ry in resources)
    my_min_d, _ = my_best
    op_min_d, _ = op_best
    behind = (my_min_d - op_min_d) >= 2

    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if behind:
            # When behind, prioritize low contest far from opponent to reduce opponent stealing.
            key = (-(od - sd), -(sd), cheb(ox, oy, rx, ry), -(rx + 31 * ry))
        else:
            # When not behind, prioritize cells where we are closer than opponent.
            key = (min(od - sd, 9999), -(sd), -cheb(ox, oy, rx, ry), -(rx + 31 * ry))
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = (cheb(nx, ny, tx, ty), man(nx, ny, tx, ty), man(nx, ny, ox, oy), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    if best_val is None:
        # All moves blocked: stay.
        return [0, 0]
    return best_move
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
        return dx if dx > dy else dy  # Chebyshev (diagonal cost 1)

    if not resources:
        return [0, 0]

    best_target = resources[0]
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        slack = op_d - my_d  # higher means we're relatively faster
        # Prefer not-slower targets; then closer to us; then deterministic coord order
        if slack >= 0:
            key = (-slack, my_d, rx, ry)
        else:
            # Still possible: deprioritize heavily and choose the "least bad" option
            key = (0, my_d + 2 * (my_d - op_d), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_dn = dist(nx, ny, tx, ty)
        op_dn = dist(ox, oy, tx, ty)

        # Main goal: keep/expand advantage to the chosen target.
        # Secondary: reduce distance to target; tertiary: deterministic order.
        advantage_next = op_dn - my_dn
        key = (-advantage_next, my_dn, dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    if best_score is None:
        # If all moves are blocked (should be rare), try to stay.
        return [0, 0]
    return [best_move[0], best_move[1]]
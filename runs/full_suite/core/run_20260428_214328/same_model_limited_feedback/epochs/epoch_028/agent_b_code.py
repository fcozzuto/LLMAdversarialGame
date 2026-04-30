def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Pick a target resource: prefer ones where we are at least as close as opponent.
    my_best = None
    best_d = 10**9
    opp_d_best = 10**9
    for rx, ry in resources:
        d1 = dist((x, y), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        if d1 <= d2:
            if d1 < best_d or (d1 == best_d and d2 < opp_d_best):
                my_best = (rx, ry)
                best_d = d1
                opp_d_best = d2
    if my_best is None and resources:
        rx, ry = min(resources, key=lambda p: (dist((x, y), p), dist((ox, oy), p)))
        my_best = (rx, ry)

    # If no resources, head toward center to avoid deadlock.
    if not my_best:
        target = (w // 2, h // 2)
    else:
        target = my_best

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to target. Secondary: prefer staying away from opponent.
        d_target = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        # Slight preference for moving toward target along the first axis to keep determinism.
        axis_pref = (0 if dx == 0 else -1 if dx < 0 else 1)  # deterministic tie-break signal
        val = (-d_target * 1000) + (d_opp * 10) + (-abs((nx - tx)) + -abs((ny - ty)) * 0) + (-axis_pref * 0.001)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
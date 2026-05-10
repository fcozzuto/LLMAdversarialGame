def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    opts = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    # Choose best target: prefer resources where we are closer than opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        adv = od - sd  # positive => we closer
        key = (-adv, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # If we are not closer to any resource, switch to a more central/nearest target to race.
    closer_exists = False
    for rx, ry in resources:
        if manh(sx, sy, rx, ry) < manh(ox, oy, rx, ry):
            closer_exists = True
            break
    if not closer_exists:
        best_t = None
        best_key = None
        for rx, ry in resources:
            sd = manh(sx, sy, rx, ry)
            od = manh(ox, oy, rx, ry)
            key = (sd, -od, rx, ry)  # nearest to us; if tied prefer farther from opponent
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t

    # One-step evaluation toward chosen target, also considering opponent distance (denial).
    best_move = (0, 0)
    best_val = None
    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = manh(nx, ny, tx, ty)
        nod = manh(ox, oy, tx, ty)
        # Also discourage moves that increase distance to the target.
        # Value: higher is better; deterministic via ties.
        val = (nod - nsd, -nsd, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Move evaluation: maximize "winning pressure" to closest contested resource.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_key = None

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue

        # For each resource, compute advantage (opponent further) and closeness.
        best_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer
            # Prefer: large adv; then small sd; then large od (harder for them); then coord tie-break.
            key = (-adv, sd, -od, rx, ry)
            if best_for_move is None or key < best_for_move:
                best_for_move = key

        if best_for_move is None:
            continue

        # Slight preference for reducing our distance to the global nearest resource.
        global_sd = min(cheb(nx, ny, r[0], r[1]) for r in resources)
        global_od = min(cheb(ox, oy, r[0], r[1]) for r in resources)
        move_key = (best_for_move, global_sd, -global_od, nx, ny)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dxm, dym)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
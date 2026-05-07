def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Choose resource where we are relatively closer than the opponent (deterministic tie-break by coords)
        best_key = None
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            key = (do - ds, -ds, -rx, -ry, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                tx, ty = rx, ry
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        # Primary: minimize our distance to target; Secondary: maximize opponent distance to us (denial); Tertiary: minimize opp-to-target
        opp_to_target = man(ox, oy, tx, ty)
        key = (-d_self, d_opp, -opp_to_target, -nx, -ny, dx, dy)
        if best is None or key > best:
            best = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]
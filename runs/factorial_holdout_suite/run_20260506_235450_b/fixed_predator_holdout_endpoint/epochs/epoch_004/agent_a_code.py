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

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            key = (do - ds, -ds, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # Prefer move that reduces our distance to target; break ties by denying opponent (increase opponent distance)
    bestm = (None, 0, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        opp_to_target = man(ox, oy, tx, ty)
        # If we are already on target, stay unless obstacle forces movement (engine keeps us if invalid anyway)
        key = (-d_self, opp_to_target - man(ox, oy, tx, ty), -d_opp, nx, ny, 0)
        if bestm[0] is None or key > bestm[0]:
            bestm = (key, dx, dy, 0)

    return [bestm[1], bestm[2]]
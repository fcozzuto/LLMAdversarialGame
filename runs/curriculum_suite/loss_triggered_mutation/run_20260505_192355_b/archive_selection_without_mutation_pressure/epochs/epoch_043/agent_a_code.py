def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_res = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (od - sd, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    self_adv = best_key[0]

    if self_adv > 0:
        dx = 0
        dy = 0
        if rx > sx:
            dx = 1
        elif rx < sx:
            dx = -1
        if ry > sy:
            dy = 1
        elif ry < sy:
            dy = -1
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if ok(nx, ny) and man(nx, ny, rx, ry) < man(sx, sy, rx, ry):
                return [ddx, ddy]
        return [0, 0]

    # Interception/denial: choose move that maximizes opponent distance advantage reversal
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd = man(nx, ny, rx, ry)
        od = man(nx, ny, ox, oy)
        # Prefer increasing distance to opponent while not moving too far from the best resource.
        val = (od - sd, -od, -sd)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
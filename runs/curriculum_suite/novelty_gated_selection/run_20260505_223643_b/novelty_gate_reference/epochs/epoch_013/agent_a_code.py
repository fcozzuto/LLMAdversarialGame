def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(int(p[0]), int(p[1])) for p in obstacles_list}

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    target = None
    if resources:
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer (or opponent is farther), tie-break deterministically
            key = (sd - od, sd, rx, ry)
            if best is None or key < best:
                best = key
                target = (rx, ry)

    if target is None:
        return [0, 0]

    tx, ty = target

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Also value distancing from opponent generally (helps vs sweep patterns)
        opp_to_self = cheb(nx, ny, ox, oy)
        # Primary: get closer to target; Secondary: deny opponent potential advantage; Tertiary: reduce distance to resources overall
        val = (nsd, (nsd - nod), -opp_to_self, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
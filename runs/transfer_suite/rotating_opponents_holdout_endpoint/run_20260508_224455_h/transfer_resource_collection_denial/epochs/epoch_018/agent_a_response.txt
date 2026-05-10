def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if (sx, sy) in obstacles or not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources where we are closer than opponent; tie-break by more slack and then nearer (sd)
        key = (od - sd, -(sd), -((rx + ry) & 7), -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = man(nx, ny, tx, ty)
        opp_nd = man(nx, ny, ox, oy)
        self_progress = man(sx, sy, tx, ty) - nd  # >0 means getting closer
        opp_progress = man(ox, oy, tx, ty) - man(nx, ny, tx, ty)  # not directly useful but deterministic tie-break
        # Value: maximize progress; minimize distance to target; maximize distance from opponent; slight preference to reduce both coordinates parity
        val = (self_progress, -nd, opp_nd, -opp_progress, -((nx + ny) & 7), -nx, -ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move
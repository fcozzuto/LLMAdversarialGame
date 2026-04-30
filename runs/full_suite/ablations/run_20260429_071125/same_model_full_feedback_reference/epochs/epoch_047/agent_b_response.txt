def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    # Pick a target that we can reach more easily than the opponent.
    # Score = opponent_distance - self_distance (prefer positive margins), tie-break: self distance then coord.
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds
            cand = (margin, -ds, -rx, -ry)
            if best is None or cand > best[0]:
                best = (cand, (rx, ry))
        tx, ty = best[1]
    else:
        # No visible resources: drift toward the center to reduce future pathing.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Greedy step: minimize distance to target; slight penalty for moving closer to opponent (denser contest).
    best_move = (None, None)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dt = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)
        # If we're contesting the target area, avoid being next to opponent unless it also improves target distance.
        # Key: (target_distance, opponent_distance_avoid, tie by coords)
        key = (dt, -dop, -nx, -ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_target = None
    best_val = None
    for tx, ty in resources:
        self_d = cheb(sx, sy, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Bias away from opponent's likely sweep row
        sweep_pen = 2 if ty == oy else 0
        val = (opp_d - self_d - sweep_pen, -self_d, -abs(ty - sy), -abs(tx - sx))
        if best_val is None or val > best_val:
            best_val = val
            best_target = (tx, ty)

    tx, ty = best_target
    best_move = (0, 0)
    best_mval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # Also keep distance advantage; deterministic preference on ties
        mval = (-d, cheb(ox, oy, nx, ny), d, dx, dy)
        if best_mval is None or mval > best_mval:
            best_mval = mval
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
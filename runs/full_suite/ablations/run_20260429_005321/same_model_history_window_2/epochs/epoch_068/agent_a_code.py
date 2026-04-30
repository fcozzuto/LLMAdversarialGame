def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def res_score(px, py, rx, ry):
        d_me = cheb(px, py, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # If we are closer than opponent, strongly favor; otherwise try to deny by contesting.
        return (d_op - d_me) * 10 - d_me + (1 if (rx == px and ry == py) else 0)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, (0, 0))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                    best = (d, (dx, dy))
        dx, dy = best[1]
        return [int(dx), int(dy)]

    best_dx, best_dy = 0, 0
    best_val = -10**18
    # One-step lookahead to maximize immediate strategic value (and deterministic tiebreak).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = -10**18
        for rx, ry in resources:
            v = res_score(nx, ny, rx, ry)
            if v > val:
                val = v
        if val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]
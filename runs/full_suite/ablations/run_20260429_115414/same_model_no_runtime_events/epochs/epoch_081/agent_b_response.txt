def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def toward(nx, ny, tx, ty):
        dx = 0 if nx == tx else (1 if tx > nx else -1)
        dy = 0 if ny == ty else (1 if ty > ny else -1)
        return dx, dy

    if not resources:
        tx, ty = (w - 1) if (sx < w - 1) else 0, (h - 1) if (sy < h - 1) else 0
        ddx, ddy = toward(sx, sy, tx, ty)
        cand = [(ddx, ddy)]
        cand += [m for m in moves if m != (ddx, ddy)]
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_score = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer, and slightly favor central-ish lanes.
        # Opponent "intercept" term: reward states where we can arrive earlier.
        center_bias = - (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)) * 0.01
        score = (do - ds) * 10.0 + center_bias - ds * 0.05
        if score > best_score:
            best_score = score
            best = (rx, ry)

    rx, ry = best
    ddx, ddy = toward(sx, sy, rx, ry)
    # Deterministic local choice: move that most reduces distance to target; tie-break by order.
    curd = cheb(sx, sy, rx, ry)
    best_move = (0, 0)
    best_dist = curd
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, rx, ry)
        if d < best_dist or (d == best_dist and (dx, dy) == (ddx, ddy)):
            best_dist = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
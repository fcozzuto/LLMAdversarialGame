def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    w = int(w); h = int(h)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if resources:
        tx, ty = resources[0]
        best = cheb(sx, sy, tx, ty)
        for r in resources[1:]:
            d = cheb(sx, sy, r[0], r[1])
            if d < best:
                best = d
                tx, ty = r[0], r[1]
    else:
        tx, ty = (0, 0)
        d0 = cheb(sx, sy, tx, ty)
        for cx, cy in [(0, h - 1), (w - 1, 0), (w - 1, h - 1)]:
            d = cheb(sx, sy, cx, cy)
            if d > d0:
                d0 = d
                tx, ty = cx, cy

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist_to_t = cheb(nx, ny, tx, ty)
        dist_to_o = cheb(nx, ny, ox, oy)
        score = -dist_to_t + 0.05 * dist_to_o
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]
def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0) or 8
    h = int(observation.get("grid_height", 0) or 0) or 8
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dist_opp = cheb(sx, sy, ox, oy)
    flee = (dist_opp <= 2 and res)

    if res:
        if flee:
            best_dist = -1
            best = (0, 0)
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                d = cheb(nx, ny, ox, oy)
                if d > best_dist:
                    best_dist = d
                    best = (dx, dy)
            return [int(best[0]), int(best[1])]
        tx, ty = min(res, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = w // 2, h // 2

    best_val = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_res = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        val = (d_res, -d_opp, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
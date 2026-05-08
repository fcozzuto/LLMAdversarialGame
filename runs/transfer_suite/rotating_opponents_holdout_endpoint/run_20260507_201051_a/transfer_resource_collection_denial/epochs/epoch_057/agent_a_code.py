def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not res:
        tx, ty = ox, oy
    else:
        best = res[0]
        best_d = cheb(sx, sy, best[0], best[1])
        for x, y in res[1:]:
            d = cheb(sx, sy, x, y)
            if d < best_d:
                best_d = d
                best = (x, y)
        tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    cur_to_t = cheb(sx, sy, tx, ty)
    cur_to_o = cheb(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        val = (cur_to_t - d_to_t) * 1000 + d_to_o - cheb(nx, ny, tx, ty)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]
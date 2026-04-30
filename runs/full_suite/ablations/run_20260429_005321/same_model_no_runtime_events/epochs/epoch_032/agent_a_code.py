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

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd_opp = cheb(sx, sy, ox, oy)

    best = (0, 0)
    best_score = -10**18

    if res:
        target = min(res, key=lambda r: cheb(sx, sy, r[0], r[1]))
        tx, ty = target
        best_opp_curd = cheb(ox, oy, tx, ty)
    else:
        tx, ty = ox, oy
        best_opp_curd = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        dist = cheb(nx, ny, tx, ty)
        curdist = cheb(sx, sy, tx, ty)
        score = -dist
        if (nx, ny) == (tx, ty):
            score += 1000
        score += 3 if dist < curdist else 0

        nd_opp = cheb(nx, ny, ox, oy)
        if best_opp_curd is not None:
            opp_next = best_opp_curd  # rough proxy; opponent likely moves similarly
            if dist <= opp_next:
                score += 20
        if nd_opp < curd_opp:
            score -= 8  # avoid approaching opponent too aggressively

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
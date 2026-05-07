def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    w = int(w) if isinstance(w, (int, float, str)) else 8
    h = int(h) if isinstance(h, (int, float, str)) else 8

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        dx = -dx if dx < 0 else dx
        dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - ds) * 100000 - ds
        if best is None or score > best_score:
            best = (rx, ry)
            best_score = score

    tx, ty = best
    best_move = (0, 0)
    best_dist = None
    best_tie = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        tie = (d, -opp_d, dx == 0 and dy == 0)
        if best_dist is None or d < best_dist or (d == best_dist and tie < best_tie):
            best_move = (dx, dy)
            best_dist = d
            best_tie = tie

    dx, dy = best_move
    return [int(dx), int(dy)]
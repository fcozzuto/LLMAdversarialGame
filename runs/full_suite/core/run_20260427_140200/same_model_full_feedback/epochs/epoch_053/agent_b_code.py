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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        dx = 0
        dy = 0
        if sx < ox and valid(sx + 1, sy):
            dx = 1
        elif sx > ox and valid(sx - 1, sy):
            dx = -1
        elif sy < oy and valid(sx, sy + 1):
            dy = 1
        elif sy > oy and valid(sx, sy - 1):
            dy = -1
        if not valid(sx + dx, sy + dy):
            for ddx, ddy in dirs:
                if valid(sx + ddx, sy + ddy):
                    dx, dy = ddx, ddy
                    break
        return [int(dx), int(dy)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    bestd = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < bestd:
            bestd = d
            best = (rx, ry)

    rx, ry = best
    best_move = (0, 0)
    best_score = -10**18

    # Simple deterministic scoring: go closer to nearest resource; avoid moves that let opponent get closer too.
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer decreasing distance; add slight preference for moves that increase opponent's distance.
        score = (-myd) + (0.15 * (opd - cheb(nx, ny, ox, oy))) + (0.25 * (opd - myd))
        if score > best_score:
            best_score = score
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]
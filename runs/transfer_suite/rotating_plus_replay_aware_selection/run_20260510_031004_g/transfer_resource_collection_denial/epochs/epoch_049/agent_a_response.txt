def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                nx, ny = sx + dx, sy + dy
                if valid(nx, ny):
                    moves.append((dx, dy))
    if not resources or not moves:
        return [0, 0]

    best = None  # (priority, self_dist, rx, ry)
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach strictly sooner; otherwise, closest.
        if sd < od:
            priority = 2
            gap = od - sd
        elif sd == od:
            priority = 1
            gap = 0
        else:
            priority = 0
            gap = -sd
        cand = (priority, gap, -sd, rx, ry)
        if best is None or cand > best:
            best = cand
    if best is None:
        return [0, 0]

    rx, ry = best[3], best[4]
    curd = cheb(sx, sy, rx, ry)

    best_move = None  # (dist_after, tie_priority, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        da = cheb(nx, ny, rx, ry)
        # Prefer decreasing distance; deterministic tie-break by coordinates.
        if da < curd:
            tp = 2
        elif da == curd:
            tp = 1
        else:
            tp = 0
        cand = (da, tp, -nx, -ny, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand

    return [int(best_move[4]), int(best_move[5])]
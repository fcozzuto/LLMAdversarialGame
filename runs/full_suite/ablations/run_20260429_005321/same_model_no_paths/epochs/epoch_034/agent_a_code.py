def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = (0, 0)
    best_score = -10**18
    fallback = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if (dx, dy) == (0, 0):
            fallback = (dx, dy)
        res_term = 0
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d = cheb(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            res_term = -dmin
        opp_term = cheb(nx, ny, ox, oy)
        score = res_term * 10 + opp_term
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if ok(sx + best[0], sy + best[1]) else [int(fallback[0]), int(fallback[1])]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        try:
            x, y = p
            obst.add((int(x), int(y)))
        except:
            continue
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        my_dist_to_best = None
        opp_dist_to_best = None
        for r in resources:
            try:
                rx, ry = r
                rx = int(rx); ry = int(ry)
            except:
                continue
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            comp = md - od
            if my_dist_to_best is None or (comp, md, rx, ry) < my_dist_to_best:
                my_dist_to_best = (comp, md, rx, ry)
                opp_dist_to_best = od
        if my_dist_to_best is None:
            opp_d = cheb(nx, ny, ox, oy)
            score = (1000000 - opp_d, -opp_d, 0)
        else:
            comp, md, rx, ry = my_dist_to_best
            opp_d = opp_dist_to_best
            # Prefer small md (near resource), large opp_d (opponent far), and deterministic tie-break.
            score = (-md, opp_d, -(rx + ry), -rx)
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
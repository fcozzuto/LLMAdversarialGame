def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            best_adv = None
            best_myd = None
            best_res = None
            for rx, ry in resources:
                dm = dist_cheb(nx, ny, rx, ry)
                do = dist_cheb(ox, oy, rx, ry)
                adv = do - dm
                key = (-(adv), dm, rx, ry)
                if best_adv is None or key < (-(best_adv), best_myd, best_res[0], best_res[1]):
                    best_adv = adv
                    best_myd = dm
                    best_res = (rx, ry)
            score = (best_adv, -best_myd, best_res[0], best_res[1], dx, dy)
        else:
            score = (-dist_cheb(nx, ny, ox, oy), 0, 0, 0, dx, dy)
        if best is None or score > best:
            best = score

    if best is None:
        return [0, 0]
    return [best[4], best[5]]
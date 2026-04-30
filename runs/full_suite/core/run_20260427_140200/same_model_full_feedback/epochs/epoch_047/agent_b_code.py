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

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def safe_bonus(nx, ny):
        # Prefer staying away from likely opponent pursuit
        d = dist_cheb(nx, ny, ox, oy)
        return d * 0.05

    def central_tendency(nx, ny):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        ddx = nx - cx
        if ddx < 0: ddx = -ddx
        ddy = ny - cy
        if ddy < 0: ddy = -ddy
        return -(ddx + ddy) * 0.01

    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            my_best = 10**9
            rel_best = -10**9
            # Target scoring: beat opponent on nearest contested resource; also prefer closer to any resource
            for rx, ry in resources:
                dme = dist_cheb(nx, ny, rx, ry)
                dop = dist_cheb(ox, oy, rx, ry)
                if dme < my_best:
                    my_best = dme
                rel = (dop - dme)  # positive means we are closer than opponent
                if rel > rel_best:
                    rel_best = rel
            score = (rel_best * 2.0) + (-my_best * 1.1) + safe_bonus(nx, ny) + central_tendency(nx, ny)
        else:
            # No visible resources: move to contest center while keeping distance from opponent
            score = safe_bonus(nx, ny) + central_tendency(nx, ny) - dist_cheb(nx, ny, ox, oy) * 0.02

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
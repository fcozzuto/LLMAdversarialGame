def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            res_best = 0
            if resources:
                m = 10**9
                for rx, ry in resources:
                    d = cheb(nx, ny, rx, ry)
                    if d < m:
                        m = d
                res_best = -m
            opp_d = cheb(nx, ny, ox, oy)
            if not resources:
                # go to a corner farthest from the opponent (deterministic fallback)
                cx = (w - 1) if ox < w // 2 else 0
                cy = (h - 1) if oy < h // 2 else 0
                res_best = -cheb(nx, ny, cx, cy)
            # Prefer reducing distance to resources, and also avoid being too close to opponent
            score = (res_best * 10) - opp_d
            cand.append((score, -dx, -dy, dx, dy))

    cand.sort()
    return [cand[-1][3], cand[-1][4]] if cand else [0, 0]
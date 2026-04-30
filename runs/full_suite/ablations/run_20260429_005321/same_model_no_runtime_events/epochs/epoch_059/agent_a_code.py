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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        resources = sorted(resources, key=lambda r: (r[0], r[1]))
        # Deterministic choice among tied moves via resource ordering.
        def best_target_dist(x, y):
            best = None
            for rx, ry in resources:
                d = cheb(x, y, rx, ry)
                if best is None or d < best:
                    best = d
            return best if best is not None else 0
        target_weight = 1.0
    else:
        target_weight = 0.0

    cx, cy = (w - 1) // 2, (h - 1) // 2

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        dist_op = cheb(nx, ny, ox, oy)
        if resources:
            dist_res = best_target_dist(nx, ny)
            score = (-target_weight * dist_res) + (0.15 * dist_op)
        else:
            dist_c = cheb(nx, ny, cx, cy)
            score = (-dist_c) + (0.10 * dist_op)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move
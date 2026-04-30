def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_delta = (0, 0)
    best_val = None

    if not resources:
        tx, ty = (3, 3) if (cheb(sx, sy, 3, 3) <= cheb(sx, sy, 4, 4)) else (4, 4)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                val = -cheb(nx, ny, tx, ty)
                if best_val is None or val > best_val:
                    best_val = val
                    best_delta = (dx, dy)
        return [best_delta[0], best_delta[1]]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        my_best = None
        for x, y in resources:
            do = cheb(ox, oy, x, y)
            ds = cheb(nx, ny, x, y)
            val = (do - ds) * 10 - ds  # maximize opponent slowness, then our quickness
            if my_best is None or val > my_best:
                my_best = val
        if best_val is None or my_best > best_val:
            best_val = my_best
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]
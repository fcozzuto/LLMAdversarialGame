def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        val = 0.0
        if resources:
            best_target = None
            best_diff = -10**18
            for tx, ty in resources:
                ds = cheb(nx, ny, tx, ty)
                do = cheb(ox, oy, tx, ty)
                diff = do - ds  # positive means we are closer (or equal)
                if diff > best_diff:
                    best_diff = diff
                    best_target = (tx, ty)
            tx, ty = best_target
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            val += 20.0 * (best_diff) - 1.2 * ds
            val += 3.0 if ds == 0 else 0.0
            val += 1.5 / (1.0 + abs((do - ds)))
            # avoid stepping into opponent-like collision zones
            dist_to_op = cheb(nx, ny, ox, oy)
            val -= 0.4 / (1.0 + dist_to_op)
        else:
            # no known resources: move to center to reduce travel time
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = -cheb(nx, ny, cx, cy)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]
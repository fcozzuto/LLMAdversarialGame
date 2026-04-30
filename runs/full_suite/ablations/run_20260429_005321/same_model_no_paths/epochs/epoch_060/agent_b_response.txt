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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obst_pen(x, y):
        pen = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in obstacles:
                    pen += 2
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        total = -near_obst_pen(nx, ny)
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # prioritize closer resources, discourage chasing where opponent is already at least as close
            denom = ds + 1
            gain = 100.0 / denom
            if dop <= ds:
                gain -= 35.0 / (dop + 1)
            # slight bias to immediate pickup
            if ds == 0:
                gain += 50.0
            total += gain

        if best is None or total > best_val:
            best = (dx, dy)
            best_val = total
        elif total == best_val and best is not None:
            # deterministic tie-breaker: fixed move order already iterates deterministically, so ignore
            pass

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
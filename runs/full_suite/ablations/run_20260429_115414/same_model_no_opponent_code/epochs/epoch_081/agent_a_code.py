def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    remaining = observation.get("remaining_resource_count", None)
    if resources and not (isinstance(remaining, (int, float)) and remaining <= 0):
        tx, ty = resources[0]
        bestd = cheb(sx, sy, tx, ty)
        for (x, y) in resources[1:]:
            d = cheb(sx, sy, x, y)
            if d < bestd:
                bestd = d
                tx, ty = x, y
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    best_tuple = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dtarget = cheb(nx, ny, tx, ty)
        ddopp = cheb(nx, ny, ox, oy)
        cand = (dtarget, -ddopp, dx, dy)
        if best_tuple is None or cand < best_tuple:
            best_tuple = cand
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        tx, ty = (w - 1 + 0) // 2, (h - 1 + 0) // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = kdist(nx, ny, tx, ty)
            if (d, dx, dy) < (best[0], best[2], best[3]):
                best = (d, 0, dx, dy)
        return [best[2], best[3]]

    best_t = None
    best_key = (10**9, 10**9)
    for rx, ry in resources:
        ds = kdist(sx, sy, rx, ry)
        do = kdist(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; slight preference for being closer to center too.
        center_bias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        key = (ds - (do * 0.7), ds + center_bias * 0.01)
        if key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    best_step = (10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = kdist(nx, ny, tx, ty)
        # If we can tie the distance, reduce distance advantage for opponent by moving away from their position.
        adv = kdist(nx, ny, ox, oy)
        key = (d1, adv, dx, dy)
        if key < best_step:
            best_step = key
    return [best_step[2], best_step[3]]
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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not resources:
        best = (0, 0)
        bestv = -1e18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -cheb(nx, ny, ox, oy) - 0.01 * cheb(nx, ny, int(cx), int(cy))
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -1e18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        best_r = -1e18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources you reach sooner than opponent (gap), otherwise still progress.
            gap = od - sd
            v = -sd + 0.7 * gap
            # Small tie-break: pull toward center to reduce wandering.
            v += -0.01 * cheb(nx, ny, int(cx), int(cy))
            if v > best_r:
                best_r = v
        if best_r > best_val:
            best_val = best_r
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
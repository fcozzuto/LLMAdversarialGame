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
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy)  # drift away if no resources
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer targets we can reach earlier (larger od-sd), then closer by our distance
        key = (od - sd, -sd, -abs(rx - (w - 1 - ox)) - abs(ry - (h - 1 - oy)))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    curd = cheb(sx, sy, tx, ty)
    best = [0, 0]
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Primary: reduce distance to target; Secondary: avoid stepping into being too close to opponent path
        # Approximation: higher is better
        v = 1000 * (curd - nd) - 2 * cheb(nx, ny, ox, oy)
        # If same progress, prefer moves that improve "race advantage" to the chosen target
        v += (cheb(ox, oy, tx, ty) - nd)
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best
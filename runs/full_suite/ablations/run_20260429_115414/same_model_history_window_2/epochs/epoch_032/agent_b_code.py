def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            sd_best = 10**18
            od_best = 10**18
            for x, y in resources:
                sd = dist(sx, sy, x, y)
                if sd < sd_best: sd_best = sd
                od = dist(ox, oy, x, y)
                if od < od_best: od_best = od
            score = (od_best - sd_best)
            # Prefer stepping closer to some resource; exact target not tracked, but monotonic via min distance after move
            after = 10**18
            for x, y in resources:
                d = dist(nx, ny, x, y)
                if d < after: after = d
            key = (-(score), after, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dself = dist(nx, ny, cx, cy)
            dopp = dist(nx, ny, ox, oy)
            key = (dself, -dopp, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                best = [dx, dy]
                break
    return best
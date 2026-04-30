def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def mdist(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None

    target = resources[0] if resources else (w // 2, h // 2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if resources:
            tr = resources[0]
            bd = mdist(nx, ny, tr[0], tr[1])
            for r in resources[1:]:
                d = mdist(nx, ny, r[0], r[1])
                if d < bd:
                    bd = d
                    tr = r
            res_d = bd
        else:
            res_d = mdist(nx, ny, target[0], target[1])

        opp_d = mdist(nx, ny, ox, oy)

        # Higher is better: closer to resources, farther from opponent; small preference for staying centered
        center_pen = mdist(nx, ny, w // 2, h // 2)
        val = (-res_d * 10) + (opp_d * 6) - center_pen

        if best is None or val > best[0]:
            best = (val, dx, dy)

    if best is not None:
        return [int(best[1]), int(best[2])]
    return [0, 0]
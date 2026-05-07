def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = None  # (primary, secondary, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            mind = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            primary = -mind
        else:
            primary = -man(nx, ny, cx, cy)

        secondary = man(nx, ny, ox, oy)

        cand = (primary, secondary, dx, dy)
        if best is None or (cand[0] > best[0]) or (cand[0] == best[0] and cand[1] > best[1]):
            best = cand

    if best is None:
        return [0, 0]
    return [best[2], best[3]]
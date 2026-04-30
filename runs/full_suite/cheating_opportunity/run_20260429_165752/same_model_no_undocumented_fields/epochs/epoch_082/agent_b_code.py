def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
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

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            myd = 10**9
            opd = 10**9
            for rx, ry in resources:
                d1 = md(nx, ny, rx, ry)
                if d1 < myd:
                    myd = d1
                d2 = md(ox, oy, rx, ry)
                if d2 < opd:
                    opd = d2
            near_bonus = 1000 if myd == 0 else 0
            v = near_bonus + (opd - myd) * 10 - myd
        else:
            cx, cy = w // 2, h // 2
            v = -md(nx, ny, cx, cy) + (-md(ox, oy, cx, cy))
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return list(best if best is not None else (0, 0))
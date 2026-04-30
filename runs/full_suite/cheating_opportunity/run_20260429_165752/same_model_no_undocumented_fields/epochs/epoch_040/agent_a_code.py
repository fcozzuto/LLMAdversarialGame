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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    legal = []
    for dx, dy in dirs:
        if free(sx + dx, sy + dy):
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            score = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            opp_pen = 0
            if (abs(nx - ox) <= 1 and abs(ny - oy) <= 1):
                opp_pen = 1000
            key = (score + opp_pen, (nx - sx) * (nx - sx) + (ny - sy) * (ny - sy))
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        key = (dist(nx, ny, cx, cy), -dist(nx, ny, ox, oy))
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]
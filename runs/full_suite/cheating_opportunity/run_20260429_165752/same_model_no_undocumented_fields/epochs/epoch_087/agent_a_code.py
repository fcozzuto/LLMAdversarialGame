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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)
    rshift = t % 9
    dirs = dirs[rshift:] + dirs[:rshift]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    if resources:
        best = None
        bestd = 10**9
        for rx, ry in resources:
            if dist(sx, sy, rx, ry) < bestd:
                bestd = dist(sx, sy, rx, ry)
                best = (rx, ry)
        target = best

    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if target is not None:
            myd = dist(nx, ny, target[0], target[1])
            oppd = dist(nx, ny, ox, oy)
            goal_score = -myd
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            myd = dist(nx, ny, cx, cy)
            oppd = dist(nx, ny, ox, oy)
            goal_score = -myd + 0.2 * oppd

        step = (dx != 0 or dy != 0)
        score = goal_score + (0.05 * oppd if target is not None else 0.2 * oppd) + (0.01 if step else 0.0)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move
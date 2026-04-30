def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best_move = (0, 0, 10**9)
        for dx, dy, nx, ny in legal:
            score = 10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Lower is better: go for resources we can reach earlier, otherwise prefer distant from opponent.
                key = myd - 0.85 * opd
                # Small tie-breaker to reduce wandering: prefer smaller myd when similar key.
                key = key * 100 + myd
                if key < score:
                    score = key
            # Secondary preference: keep moving roughly toward opponent side (more commitment after bad epoch)
            toward = cheb(nx, ny, w - 1, h - 1) - cheb(nx, ny, 0, 0)
            score2 = score + 0.01 * toward
            if score2 < best_move[2]:
                best_move = (dx, dy, score2)
        return [int(best_move[0]), int(best_move[1])]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy, nx, ny in legal:
        d = cheb(nx, ny, cx, cy)
        if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
            best = (d, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]
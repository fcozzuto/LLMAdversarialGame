def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best_move = None
    for dx, dy, nx, ny in legal:
        move_best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # positive means we are closer than opponent at this step
            # Prefer largest margin, then smaller ds, then larger do, then deterministic by coords
            cand = (margin, -ds, do, -rx, -ry)
            if move_best is None or cand > move_best:
                move_best = cand
        if best_move is None or move_best > best_move[0]:
            best_move = (move_best, dx, dy)
        elif move_best[0] == move_best[0]:
            # deterministic tie-breaker on move direction
            if (dx, dy) < (best_move[1], best_move[2]):
                best_move = (move_best, dx, dy)

    return [int(best_move[1]), int(best_move[2])]
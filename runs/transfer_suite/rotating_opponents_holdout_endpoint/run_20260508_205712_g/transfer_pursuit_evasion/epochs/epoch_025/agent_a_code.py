def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy
    role = observation.get("self_role", "pursuer")
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        obst_adj = 0
        for adx, ady in moves:
            if (nx + adx, ny + ady) in obstacles:
                obst_adj += 1
        if role == "evader":
            # maximize distance; prefer staying in center; avoid clutter/obstacles
            center_pen = cheb(nx, ny, int(cx), int(cy))
            score = (-dist) + (-0.25 * center_pen) + (0.15 * obst_adj)
            better = best is None or score < best_score
        else:
            # minimize distance; avoid obstacles near the move (tiebreak)
            score = dist + (0.15 * obst_adj)
            better = best is None or score < best_score
        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
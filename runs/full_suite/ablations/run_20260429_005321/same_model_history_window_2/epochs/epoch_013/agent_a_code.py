def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    obstacles = observation.get("obstacles") or []
    obst = set((int(p[0]), int(p[1])) for p in obstacles)
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose target: best for us and worst for opponent (maximize opponent advantage loss)
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            dm = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            ahead = do - dm
            key = (ahead, -dm, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources: go to corner opposite opponent-ish
        tx = 0 if ox >= w // 2 else w - 1
        ty = 0 if oy >= h // 2 else h - 1

    # Prefer move that reduces our distance to target; avoid obstacles; lightly penalize cells near opponent
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    curd = cheb(sx, sy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        nd = cheb(nx, ny, tx, ty)
        oppd = cheb(nx, ny, ox, oy)
        # Deterministic scoring
        score = (curd - nd) * 1000 + oppd - (1 if (dx == 0 and dy == 0) else 0) + (-dx) * 0.01 + (-dy) * 0.0001
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not isinstance(dx, int) or not isinstance(dy, int):
        return [0, 0]
    return [dx, dy]
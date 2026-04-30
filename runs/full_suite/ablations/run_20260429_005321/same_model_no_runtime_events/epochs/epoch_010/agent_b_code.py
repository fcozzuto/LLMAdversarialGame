def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            rx, ry = r[0], r[1]
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        bx, by = (w - 1) // 2, (h - 1) // 2
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            adv = opd - myd
            if best is None or adv > best or (adv == best and myd < dist(sx, sy, bx, by)):
                best = adv
                bx, by = rx, ry
        tx, ty = bx, by
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_score = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        myd = dist(nx, ny, tx, ty)
        opd = dist(ox, oy, tx, ty)
        next_opd = opd  # opponent move unknown; compare to opponent current distance
        score = (next_opd - myd) * 10 - myd
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
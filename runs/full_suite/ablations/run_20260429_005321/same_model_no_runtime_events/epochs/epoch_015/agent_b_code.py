def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

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

    best_t = (ox, oy)
    best_d = cheb(sx, sy, ox, oy)
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < best_d:
            best_d = d
            best_t = (rx, ry)

    tx, ty = best_t
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        score = d
        if score == d:
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
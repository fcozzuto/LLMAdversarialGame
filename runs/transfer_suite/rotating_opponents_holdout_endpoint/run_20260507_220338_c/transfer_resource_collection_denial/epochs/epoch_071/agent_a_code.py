def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            q = (p[0], p[1])
            if q not in obst:
                res.append(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]

    if (sx, sy) in obst:
        tx, ty = ox, oy
    elif res:
        best = None
        bd = None
        for rx, ry in res:
            d = man(sx, sy, rx, ry)
            if bd is None or d < bd or (d == bd and (rx, ry) < best):
                bd = d
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = ox, oy

    best_move = moves[0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        score = man(nx, ny, tx, ty)
        if (nx, ny) == (tx, ty):
            score -= 1000000
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
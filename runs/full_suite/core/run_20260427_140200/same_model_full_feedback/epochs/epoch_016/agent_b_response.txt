def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            diff = d_op - d_me  # higher means we are relatively closer
            # Prefer positive diff; if all negative, pick least d_me
            key = (diff, -d_me, -(rx + ry) * 0)  # deterministic tiebreaker
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        tx, ty = (0, 0) if (sx + sy) % 2 == 0 else (w - 1, h - 1)

    best_move = (0, 0, sx, sy)
    best_score = None
    for dx, dy, nx, ny in legal:
        d_to = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, nx, ny)
        # Primary: get closer to chosen target; Secondary: keep distance from opponent
        score = (-d_to, d_op, -(nx * 9 + ny), -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]
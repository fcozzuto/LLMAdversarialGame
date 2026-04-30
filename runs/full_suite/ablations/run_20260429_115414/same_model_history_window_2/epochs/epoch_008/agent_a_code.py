def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

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

    viable = []
    for r in resources:
        rx, ry = r[0], r[1]
        if inb(rx, ry) and (rx, ry) not in blocked:
            viable.append((rx, ry))

    def best_target():
        if not viable:
            return None
        best = None
        best_key = None
        for rx, ry in viable:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            belt = abs((rx + ry) - (sx + sy))
            key = (-(od - myd), myd, belt, rx, ry)  # maximize od-myd, then minimize myd
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tgt = best_target()
    if tgt is None:
        # deterministic fallback: move toward center-ish, avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        tx, ty = tgt

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # prefer moves that keep/extend contest advantage and reduce distance to target
        score = (myd, -((od - myd)), abs((tx + ty) - (nx + ny)), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
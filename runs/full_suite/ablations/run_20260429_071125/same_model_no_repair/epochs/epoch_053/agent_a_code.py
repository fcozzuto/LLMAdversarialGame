def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer contested (opd - myd), then nearer to me
        cand = (opd - myd, -myd, rx, ry)
        if best is None or cand > best[0]:
            best = (cand, (rx, ry))
    tx, ty = best[1]

    # Move that reduces my distance to target; break ties by reducing opponent distance.
    best_move = None
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        # Secondary: how much closer to target than staying (implicit via myd)
        cand = (-myd, -opd, dx, dy)
        if best_move is None or cand > best_move[0]:
            best_move = (cand, (dx, dy))
    return [int(best_move[1][0]), int(best_move[1][1])]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = [tuple(r) for r in (observation.get("resources") or [])]
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

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        for dx, dy, nx, ny in legal:
            best_for_move = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                diff = opd - myd
                key = (diff, -myd)
                if best_for_move is None or key > best_for_move:
                    best_for_move = key
            if best is None or best_for_move > best:
                best = best_for_move
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_move = (0, 0)
    best_key = None
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, ox, oy)
        key = (-myd, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
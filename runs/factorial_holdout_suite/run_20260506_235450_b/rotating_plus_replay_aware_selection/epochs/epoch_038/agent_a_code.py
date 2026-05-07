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

    if not resources:
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Phase 1: any resource we can reach no later than opponent -> fastest win
        if ds <= do:
            key = (0, ds, -do, rx, ry)
        else:
            # Phase 2: otherwise choose the best race: maximize our advantage, then reduce our ETA
            key = (1, -(do - ds), ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    best_move = None
    best_key2 = None
    for dx, dy, nx, ny in legal:
        # prefer moves that reduce our distance; tie-break with improving contest score
        d2s = cheb(nx, ny, tx, ty)
        d2o = cheb(ox, oy, tx, ty)
        key2 = (d2s, -(d2o - d2s), abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_key2 is None or key2 < best_key2:
            best_key2 = key2
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
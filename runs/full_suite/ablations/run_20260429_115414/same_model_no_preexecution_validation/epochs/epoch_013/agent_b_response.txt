def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        try:
            px, py = int(p[0]), int(p[1])
            obs_set.add((px, py))
        except:
            pass

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y): return inb(x, y) and (x, y) not in obs_set

    # Choose best contested target: prefer where we are relatively closer.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # primary: who is closer (od-sd). secondary: smaller sd. tertiary: lexicographic.
        key = (od - sd, -sd, -((rx - w // 2) * (rx - w // 2) + (ry - h // 2) * (ry - h // 2)), rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    oppd = cheb(ox, oy, tx, ty)
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        # Score: minimize our distance to target; maximize relative advantage; add small tie-breakers.
        rel = oppd - myd
        center = -((nx - w // 2) * (nx - w // 2) + (ny - h // 2) * (ny - h // 2))
        score = (-(myd), rel, center, -abs(nx - ox) - abs(ny - oy), -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
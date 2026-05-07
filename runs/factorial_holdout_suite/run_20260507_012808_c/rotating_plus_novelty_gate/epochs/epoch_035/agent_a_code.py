def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    def clamp(v, lo, hi):
        return lo if v < lo else (hi if v > hi else v)

    sx = clamp(int(sx), 0, w - 1)
    sy = clamp(int(sy), 0, h - 1)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources") or []
    target = None
    if resources:
        bestd = None
        for r in resources:
            try:
                tx, ty = int(r[0]), int(r[1])
            except:
                continue
            if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
                continue
            d = abs(tx - sx)
            dd = abs(ty - sy)
            if dd > d:
                d = dd
            if bestd is None or d < bestd or (d == bestd and (tx, ty) < target):
                bestd = d
                target = (tx, ty)

    if target is None:
        target = ((w - 1) // 2, (h - 1) // 2)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_t = cheb(nx, ny, target[0], target[1])
        d_o = cheb(nx, ny, int(ox), int(oy))
        score = -d_t + 0.08 * d_o
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    if not valid(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return best_move
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = (w // 2, h // 2)
    mid = ((sx + ox) // 2, (sy + oy) // 2)
    tx, ty = (center[0] * 2 + mid[0]) // 3, (center[1] * 2 + mid[1]) // 3
    best = None
    best_score = -10**18
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        if d1 <= d2 + 1:
            s = (d2 - d1) * 10 - d1
            if s > best_score:
                best_score = s
                best = (rx, ry)
    if best is not None:
        tx, ty = best
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        val = -d * 5 + (do * 2)
        if resources:
            # small bonus for stepping closer to some resource likely to be taken
            for rx, ry in resources[:8]:
                if (rx, ry) in obstacles:
                    continue
                val += max(0, 3 - cheb(nx, ny, rx, ry)) - max(0, 2 - cheb(ox, oy, rx, ry))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    dx, dy = best_move
    nx, ny = sx + dx, sy + dy
    if legal(nx, ny):
        return [dx, dy]
    return [0, 0]
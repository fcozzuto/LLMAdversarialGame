def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for o in obstacles:
        try:
            obs.add((int(o[0]), int(o[1])))
        except Exception:
            pass

    res = []
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
            res.append((rx, ry))
        except Exception:
            pass

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if (x, y) in obs:
        pass
    if (x, y) in set(res):
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    def min_res_dist(px, py):
        if not res:
            return cheb(px, py, w - 1, h - 1)  # deterministic fallback
        best = 10**9
        for rx, ry in res:
            d = cheb(px, py, rx, ry)
            if d < best:
                best = d
        return best

    def obstacle_pressure(nx, ny):
        p = 0
        # discourage moving near obstacles; deterministic local check
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            tx, ty = nx + dx, ny + dy
            if (tx, ty) in obs:
                p += 1
        return p

    my_opp_dist_now = cheb(x, y, ox, oy)
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        my_d = min_res_dist(nx, ny)
        op_d = min_res_dist(ox, oy)
        # aim to reduce my distance vs opponent; also reduce distance to opponent slightly
        adv = (op_d - my_d) - 0.15 * obstacle_pressure(nx, ny) - 0.02 * cheb(nx, ny, ox, oy) + 0.01 * my_opp_dist_now
        key = (round(-adv, 6), my_d, -cheb(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
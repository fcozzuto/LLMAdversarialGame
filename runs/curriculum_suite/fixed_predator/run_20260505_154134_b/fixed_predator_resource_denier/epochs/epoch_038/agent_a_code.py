def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

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

    res = [(rx, ry) for rx, ry in resources if (rx, ry) not in obs]
    if not res:
        cx, cy = w // 2, h // 2
        best = [0, 0]
        bestv = None
        for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                v = -cheb(nx, ny, cx, cy)
                if bestv is None or v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx, cy = w // 2, h // 2
    best_move = [0, 0]
    best_key = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_self = None
        d_opp = None
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            if d_self is None or ds < d_self:
                d_self = ds
            do = cheb(ox, oy, rx, ry)
            if d_opp is None or do < d_opp:
                d_opp = do
        score_adv = d_opp - d_self
        center_bias = -cheb(nx, ny, cx, cy)
        opp_to_me = -cheb(nx, ny, ox, oy)
        key = (score_adv, center_bias, opp_to_me, -d_self, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_key = None
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if inb(tx, ty) and (tx, ty) not in obs:
                res.append((tx, ty))
    if not res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (inb(nx, ny) and (nx, ny) not in obs):
            continue
        self_d = 10**9
        opp_d = 10**9
        for tx, ty in res:
            sd = man((nx, ny), (tx, ty))
            od = man((ox, oy), (tx, ty))
            if od - sd > (opp_d - self_d):
                self_d, opp_d = sd, od
            elif od - sd == (opp_d - self_d):
                if sd < self_d or (sd == self_d and od < opp_d):
                    self_d, opp_d = sd, od
        key = (-(opp_d - self_d), self_d)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
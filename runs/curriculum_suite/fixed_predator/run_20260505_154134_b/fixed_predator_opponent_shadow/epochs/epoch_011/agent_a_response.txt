def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(px, py):
        if not resources:
            return None
        best = None
        best_key = None  # (self_d - opp_d, self_d, opp_d, -sum_coords)
        for cx, cy in resources:
            self_d = cheb(px, py, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # Want us significantly closer than opponent; otherwise still go toward "less contested"
            key = (self_d - opp_d, self_d, opp_d, -(cx + cy))
            if best_key is None or key < best_key:
                best_key = key
                best = (cx, cy)
        return best

    target = best_target(sx, sy)
    if target is None:
        return [0, 0]

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]

    best_move = [0, 0]
    best_key = None
    for mx, my in dirs:
        ax, ay = sx + mx, sy + my
        if not valid(ax, ay):
            continue
        t2 = best_target(ax, ay)
        if t2 is None:
            continue
        tx2, ty2 = t2
        self_d = cheb(ax, ay, tx2, ty2)
        opp_d = cheb(ox, oy, tx2, ty2)
        key = (self_d - opp_d, self_d, -cheb(sx, sy, tx2, ty2), mx * 2 + my)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [mx, my]
    return best_move
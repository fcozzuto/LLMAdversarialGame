def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    def obstacle_penalty(x, y):
        # Prefer staying away from obstacles without full path search
        pen = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                return 10**6
            if d == 1:
                pen += 4
            elif d == 2:
                pen += 1
        return pen

    # If resources exist, bias toward nearest/away; otherwise focus on pursuit/evasion.
    resources = observation.get("resources") or []
    if resources:
        if pursuer:
            rx, ry = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
        else:
            rx, ry = max(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
    else:
        rx = ry = None

    best = None
    best_val = -10**18 if pursuer else 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        op = obstacle_penalty(nx, ny)
        if pursuer:
            # Intercept: minimize distance; break ties by higher mobility and lower obstacle penalty.
            val = (-dist * 100) + (mob * 3) - op
        else:
            # Evade: maximize distance; also prefer corners by mildly biasing toward farthest corner.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner = max(corners, key=lambda c: cheb(c[0], c[1], nx, ny))
            corner_dist = cheb(corner[0], corner[1], nx, ny)
            res_bias = 0
            if rx is not None:
                res_bias = -cheb(nx, ny, rx, ry) if pursuer else cheb(nx, ny, rx, ry)
            val = (dist * 100) + (corner_dist * 2) + (mob * 3) + (res_bias * 0.5) - op
        # Deterministic tie-break: lexicographic (dx,dy) preference toward staying closer to opponent for pursuer, away for evader.
        if best is None or (val > best_val if pursuer else val < best_val) or (val == best_val and (dx, dy) < tuple(best)):
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    # resource direction hint
    if resources:
        if pursuer:
            rx, ry = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
        else:
            rx, ry = max(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
    else:
        rx, ry = None, None

    best_move = [0, 0]
    best_val = -10**18 if pursuer else 10**18

    # 1-step greedy with simple 2-step lookahead to break loops
    for dx1, dy1 in dirs:
        x1, y1 = sx + dx1, sy + dy1
        if not valid(x1, y1):
            continue
        d1 = cheb(x1, y1, ox, oy)
        m1 = mobility(x1, y1)
        if rx is not None:
            dr = cheb(x1, y1, rx, ry)
        else:
            dr = 0

        # approximate "next best" distance from our position after opponent capture not modeled;
        # instead, reduce opponent distance further for pursuer / increase for evader via one-ply recoil
        worst_next = d1 if pursuer else -d1
        for dx2, dy2 in dirs:
            x2, y2 = x1 + dx2, y1 + dy2
            if not valid(x2, y2):
                continue
            d2 = cheb(x2, y2, ox, oy)
            if pursuer:
                if d2 < worst_next:
                    worst_next = d2
            else:
                if d2 > worst_next:
                    worst_next = d2

        # score shaping: pursuer wants smaller distance; evader wants larger distance
        if pursuer:
            val = (-worst_next) * 100 + (m1 * 3) - (d1 * 2) - (dr * 0.1 if resources else 0)
            if val > best_val:
                best_val = val
                best_move = [dx1, dy1]
        else:
            # also bias toward farthest corner away from pursuer (deterministic)
            c = max(corners, key=lambda p: cheb(p[0], p[1], ox, oy))
            dc = cheb(x1, y1, c[0], c[1])
            val = (worst_next) * 100 + (dc * 0.5) + (m1 * 3) - (d1 * 2) + (dr * 0.1 if resources else 0)
            if val < best_val:
                best_val = val
                best_move = [dx1, dy1]

    return [int(best_move[0]), int(best_move[1])]
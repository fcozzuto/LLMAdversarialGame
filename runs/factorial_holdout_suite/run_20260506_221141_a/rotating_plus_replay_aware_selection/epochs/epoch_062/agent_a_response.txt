def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        corners = [(0, 0), (0, gh - 1), (gw - 1, 0), (gw - 1, gh - 1)]
        tx, ty = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -man(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        cell_best = -10**18
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; also prefer moving closer.
            v = (opp_d - self_d) * 100 - self_d
            cell_best = v if v > cell_best else cell_best

        # Micro-penalize stepping into worse neighborhood (avoid obstacles by favoring fewer blocked options)
        blocked = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if not legal(ax, ay):
                blocked += 1
        v = cell_best - blocked * 0.5

        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best
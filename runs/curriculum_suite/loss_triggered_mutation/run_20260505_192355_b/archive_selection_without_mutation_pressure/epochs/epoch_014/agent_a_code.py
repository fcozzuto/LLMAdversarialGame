def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def edge_bonus(x, y):
        d = min(x, w - 1 - x, y, h - 1 - y)
        return 4 if d <= 1 else 0

    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy))
    if not legal_moves:
        return [0, 0]

    if not resources:
        # Deterministically move toward opponent while preferring edges.
        best = None
        bestv = -10**18
        for dx, dy in legal_moves:
            nx, ny = sx + dx, sy + dy
            v = -man(nx, ny, ox, oy) + edge_bonus(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Score each candidate move by the best resource "steal potential".
    best = legal_moves[0]
    bestv = -10**18
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        # Avoid being too close to opponent unless you can take a resource immediately.
        opp_adj = 1 if man(nx, ny, ox, oy) <= 2 else 0
        vmax = -10**18
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                v = 10**6 - self_d
            else:
                # Positive if self is closer than opponent.
                v = 20 * (opp_d - self_d) - 2 * self_d + edge_bonus(rx, ry)
            if v > vmax:
                vmax = v
        vmove = vmax - 6 * opp_adj + edge_bonus(nx, ny)
        if vmove > bestv:
            bestv = vmove
            best = (dx, dy)

    return [best[0], best[1]]
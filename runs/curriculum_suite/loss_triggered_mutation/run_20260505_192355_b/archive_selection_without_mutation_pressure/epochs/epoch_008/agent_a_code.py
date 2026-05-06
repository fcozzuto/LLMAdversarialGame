def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    legal_moves = [(dx, dy) for dx, dy in moves if legal(sx + dx, sy + dy)]
    if not legal_moves:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def edge_bonus(x, y):
        d = min(x, w - 1 - x, y, h - 1 - y)
        return 0 if d >= 2 else (3 - d)

    best = legal_moves[0]
    bestv = -10**18

    if not resources:
        for dx, dy in legal_moves:
            nx, ny = sx + dx, sy + dy
            v = edge_bonus(nx, ny) - man(nx, ny, ox, oy) * 0.01
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        mydmin = 10**9
        opp_away = 0
        take_soon = 0
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if myd < mydmin:
                mydmin = myd
            gain = od - myd  # positive if we are closer than opponent
            if gain > 0:
                if myd == 0:
                    take_soon += 100
                opp_away += gain
        # Prefer immediate pickup, then maximize being closer than opponent, then minimize own distance.
        v = take_soon + opp_away * 2.0 - mydmin * 1.0 + edge_bonus(nx, ny) * 0.5
        if v > bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]
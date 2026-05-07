def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = set(tuple(r) for r in (observation.get("resources", []) or []))

    dxs = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if (sx, sy) in resources:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in resources:
            return [dx, dy]
        if not resources:
            return [dx, dy]

        # pick resource that maximizes "we're closer than opponent" then proximity to it
        best_margin = None
        for rx, ry in resources:
            self_d = manh(nx, ny, rx, ry)
            opp_d = manh(nx, ny, rx, ry)
            # opponent is closer if opp_d < self_d; we prefer positive (opp - self)
            margin = (opp_d - self_d, -self_d)
            if best_margin is None or margin > best_margin:
                best_margin = margin

        # also incorporate how the move changes distances to opponent overall (avoid handing resources)
        opp_dist = manh(nx, ny, ox, oy)
        self_dist = manh(nx, ny, ox, oy)  # same metric; kept for tuple shape consistency
        cand = (best_margin[0], best_margin[1], -opp_dist, dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[3]), int(best[4])]
def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in role) or ("purs" in opp_role and "evad" not in role)

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for mx, my in moves:
            nx, ny = x + mx, y + my
            if inside(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        dist = d2(nx, ny)
        md = mobility(nx, ny)

        # pursuer: minimize distance; evader: maximize distance
        sign = -1.0 if pursuer else 1.0
        score = sign * dist

        # slight bias to corners for evader, mild to center for pursuer
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        cornerish = -((nx - cx) ** 2 + (ny - cy) ** 2)
        if pursuer:
            cornerish *= -0.0005
        else:
            cornerish *= 0.0005

        # discourage low-mobility trapping
        score += (0.02 if pursuer else 0.03) * md
        score += cornerish

        # deterministic tie-break: prefer staying still, then lexicographic by (dx,dy)
        key = (score, 0 if (dx == 0 and dy == 0) else 1, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
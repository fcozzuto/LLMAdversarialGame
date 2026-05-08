def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    res = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    # Choose a target we are more likely to secure first.
    best = None
    for rx, ry in res:
        du = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # prefer we arrive earlier; then closer for us; then deterministic coord tie-break
        key = (-(do - du), du, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    (tx, ty) = best[1]

    # Opponent greedy toward their nearest resource (deterministic).
    def opp_step(px, py):
        target = None
        bestd = None
        for rx, ry in res:
            d = md(px, py, rx, ry)
            if bestd is None or (d, rx, ry) < (bestd, target[0], target[1]):
                bestd = d; target = (rx, ry)
        rx, ry = target
        bestm = (0, 0); bestk = (10**9, 10**9, 10**9)
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = px + ddx, py + ddy
                if inb(nx, ny) and (nx, ny) not in obs:
                    d = md(nx, ny, rx, ry)
                    k = (d, abs(ddx), abs(ddy), ddx, ddy)
                    if k < bestk:
                        bestk = k; bestm = (ddx, ddy)
        return bestm

    # Evaluate candidate self moves with one-step lookahead.
    best_move = (0, 0); best_score = None
    for dx, dy in legal:
        nsx, nsy = sx + dx, sy + dy
        my_d = md(nsx, nsy, tx, ty)
        odx, ody = opp_step(ox, oy)
        nosx, nosy = ox + odx, oy + ody
        opp_d = md(nosx, nosy, tx, ty)

        capture_bonus = -0.01 if (nsx, nsy) == (tx, ty) else 0.0  # minimize best_score
        score = (my_d - opp_d * 0.35) + capture_bonus
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
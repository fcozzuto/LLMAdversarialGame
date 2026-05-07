def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = min(valid, key=lambda m: (md(m[2], m[3], tx, ty), valid.index(m)))
        return [best[0], best[1]]

    res = [tuple(r) for r in resources]
    opp0 = (ox, oy)

    # Prefer immediate resource grabs; otherwise choose move that maximizes lead on some resource.
    best_move = valid[0]
    best_score = -10**18

    for (dx, dy, nx, ny) in valid:
        if (nx, ny) in res:
            my_gain = 10**9
            if my_gain > best_score:
                best_score = my_gain
                best_move = (dx, dy, nx, ny)
            continue

        local_best = -10**18
        for (rx, ry) in res:
            myd = md(nx, ny, rx, ry)
            opd = md(opp0[0], opp0[1], rx, ry)
            # If we are closer, this is good; if opponent is closer, discourage.
            lead = opd - myd
            # Tie-break toward closer resources and slightly toward reducing opponent options.
            s = lead * 100 - myd * 3 + (-md(opp0[0], opp0[1], rx, ry)) * 0.2
            if s > local_best:
                local_best = s
        # Mild bias: avoid dithering; staying still only if it's best.
        if dx == 0 and dy == 0:
            local_best -= 1
        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]
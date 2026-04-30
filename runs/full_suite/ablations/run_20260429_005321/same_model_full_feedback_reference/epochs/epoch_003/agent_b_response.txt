def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {tuple(p) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    us = (sx, sy)
    op = (ox, oy)

    if not resources:
        # Move to reduce distance to opponent's corner-diagonal-ish target
        tx, ty = (0, h - 1) if (ox + oy) > (sx + sy) else (w - 1, 0)
        best = (-10**18, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = man((nx, ny), (tx, ty))
            s = -d
            if s > best[0] or (s == best[0] and (dx, dy) < best[1]):
                best = (s, (dx, dy))
        return [best[1][0], best[1][1]]

    # Evaluate next position against best resource we can contest
    res = [tuple(r) for r in resources]
    best_move = (0, 0)
    best_score = -10**18

    # Small preference to avoid edges late
    edge_pref = 0.02 * (w + h)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        npos = (nx, ny)

        # Choose the best resource for this hypothetical move
        local_best = -10**18
        for r in res:
            us_d = man(npos, r)
            op_d = man(op, r)

            # Contention: reward being closer than opponent; punish if opponent closer
            adv = op_d - us_d  # positive if we are closer
            # Go toward it, but strongly prefer contested items
            s = (adv * 120) - (us_d * 2.2) + (op_d * 0.15)

            # Tie-break consistent: lexicographic on resource coordinates
            # (encode by subtracting tiny term based on coords)
            s -= 0.0001 * (r[0] * 10 + r[1])
            if s > local_best:
                local_best = s

        # Mild anti-edge to keep options open
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
        s_total = local_best + edge * edge_pref * 0.001

        if s_total > best_score or (s_total == best_score and (dx, dy) < best_move):
            best_score = s_total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
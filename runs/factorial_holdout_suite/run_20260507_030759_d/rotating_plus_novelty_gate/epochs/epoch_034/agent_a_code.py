def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res_set = set(tuple(r) for r in resources)

    # If standing on a resource (and not on an obstacle), collect.
    if (sx, sy) in res_set and (sx, sy) not in obstacles:
        return [0, 0]

    dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                dirs.append((dx, dy))
    if not dirs:
        return [0, 0]

    if not resources:
        # Drift away from opponent toward the farthest corner.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            val = (abs(cx - ox) - abs(cx - sx), -(abs(cx - sx) + abs(cy - sy)))
            if best is None or val > best[0]:
                best = (val, (cx, cy))
        tx, ty = best[1]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Evaluate each move by immediate advantage over opponent to the best reachable target.
    best_move = (None, -10**18, 10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy

        # Prefer targets where we are closer than opponent; otherwise, minimize opponent closeness.
        cur_best_adv = -10**18
        cur_best_selfd = 10**9
        cur_best_oppd = 10**9
        for rx, ry in resources:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)

            # Advantage: being closer by margin; strong bonus if we are strictly closer.
            adv = (od - sd)
            if adv > cur_best_adv or (adv == cur_best_adv and (sd < cur_best_selfd or (sd == cur_best_selfd and od < cur_best_oppd))):
                cur_best_adv, cur_best_selfd, cur_best_oppd = adv, sd, od

        # Add a small tie-break to avoid moving adjacent when the advantage is poor.
        near_opp = (abs(nx - ox) + abs(ny - oy) <= 2)
        near_pen = -1 if near_opp else 0

        # Also prefer moves that reduce our distance to the best target even if both are far.
        primary = cur_best_adv + near_pen
        secondary = cur_best_selfd

        if primary > best_move[1] or (primary == best_move[1] and secondary < best_move[2]):
            best_move = ((dx, dy), primary, secondary)

    return [best_move[0][0], best_move[0][1]]
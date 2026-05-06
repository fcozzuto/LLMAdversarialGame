def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cd(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # keep distance from opponent while moving toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            key = (cd((nx, ny), (cx, cy)), -cd((nx, ny), (ox, oy)), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Target selection: maximize advantage at reachable resources; add slight preference to deny opponent
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        my_pos = (nx, ny)
        opp_pos = (ox, oy)

        # choose best resource for this move
        best_for_move = None
        for rx, ry in resources:
            target = (rx, ry)
            my_d = cd(my_pos, target)
            opp_d = cd(opp_pos, target)

            # If we are at least as close as opponent, good.
            # If opponent is closer, still consider if we can become closer after this move.
            adv = opp_d - my_d

            # Denial pressure: prefer targets closer to opponent than to us (so we can contest)
            deny = -cd(opp_pos, target)

            # tie-breakers deterministic by coordinates
            key = (-(adv), -deny, my_d, opp_d, rx, ry)
            if best_for_move is None or key < best_for_move:
                best_for_move = key

        # Combine into a single deterministic score for comparing moves
        # Lower key is better; use that key as negative score proxy.
        if best_for_move is not None:
            my_key = best_for_move
            if best_score is None or my_key < best_score:
                best_score = my_key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
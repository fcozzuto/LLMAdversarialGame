def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x0, y0 = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation["resources"]
    obst = observation["obstacles"]
    obstacles = set((p[0], p[1]) for p in obst)
    resources = set((p[0], p[1]) for p in res)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if not resources:
        # No resources left: move toward center to reduce opponent trapping (deterministic).
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = None
        for dx, dy in deltas:
            nx, ny = x0 + dx, y0 + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                v = d2(nx, ny, cx, cy)
                if bestv is None or v < bestv:
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]]

    # Evaluate each move by best resource advantage and proximity.
    best_move = (0, 0)
    best_score = None
    best_tie_dist = None
    for dx, dy in deltas:
        nx, ny = x0 + dx, y0 + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_dmin = None
        my_to_target_adv = -10**18
        my_pick_score = 0

        for rx, ry in resources:
            myd = d2(nx, ny, rx, ry)
            oppd = d2(ox, oy, rx, ry)
            adv = oppd - myd  # positive means I'm closer than opponent
            # Emphasize immediate capture then advantage, then closeness
            if my_dmin is None or myd < my_dmin:
                my_dmin = myd
            if adv > my_to_target_adv:
                my_to_target_adv = adv
                # base on advantage and whether capturing this step
            if (nx, ny) == (rx, ry):
                my_pick_score = 10**9 + adv

        score = my_to_target_adv + (0 if my_pick_score else 0) - (my_dmin if my_dmin is not None else 0) * 0.01 + my_pick_score
        # Deterministic tie-breaker: prefer smaller my_dmin, then fixed delta order already preserved.
        if best_score is None or score > best_score or (score == best_score and my_dmin is not None and (best_tie_dist is None or my_dmin < best_tie_dist)):
            best_score = score
            best_move = (dx, dy)
            best_tie_dist = my_dmin

    return [best_move[0], best_move[1]]
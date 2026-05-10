def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def role_is_purs(role):
        r = (role or "").lower()
        if "purs" in r:
            return True
        if "evad" in r:
            return False
        return None

    sr = role_is_purs(observation.get("self_role"))
    orr = role_is_purs(observation.get("opponent_role"))
    if sr is None:
        sr = (orr is False)
    i_am_pursuer = bool(sr)
    opp_is_pursuer = bool(orr) if orr is not None else (not i_am_pursuer)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_opp_move(px, py, target_x, target_y, opp_should_approach):
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                continue
            d2 = (nx - target_x) * (nx - target_x) + (ny - target_y) * (ny - target_y)
            v = -d2 if opp_should_approach else d2
            if bestv is None or v > bestv:
                bestv = v
                best = (nx, ny)
        return best if best is not None else (px, py)

    # Score: if we are pursuer, minimize our distance after one-ply; if evader, maximize.
    # Use a small 2-ply with deterministic opponent prediction.
    def score_after(myx, myy, oppx, oppy, my_move):
        if i_am_pursuer:
            my_target = (oppx, oppy)
            opp_should_approach = opp_is_pursuer  # opponent pursuer approaches us
            # opponent targets us if it is pursuer, else targets to run away from us
            opp_next = best_opp_move(oppx, oppy, myx, myy, opp_should_approach)
            d2 = (myx - opp_next[0]) * (myx - opp_next[0]) + (myy - opp_next[1]) * (myy - opp_next[1])
            return -d2
        else:
            my_should_approach = False
            opp_should_approach = opp_is_pursuer
            opp_next = best_opp_move(oppx, oppy, myx, myy, opp_should_approach)
            d2 = (myx - opp_next[0]) * (myx - opp_next[0]) + (myy - opp_next[1]) * (myy - opp_next[1])
            return d2

    best_move = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Tie-break deterministically by preferring moves that keep us inside and reduce chance of sticking.
        v = score_after(nx, ny, ox, oy, (dx, dy))
        # Encourage moving toward a corner when evading to fit evasion_corner archetype.
        if not i_am_pursuer:
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            dcorner = min((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy) for cx, cy in corners)
            v += 0.001 * (-dcorner)  # smaller corner distance is better for evader to commit
        # Encourage wall-avoidance slightly (deterministic).
        wall_pen = min(nx, w - 1 - nx, ny, h - 1 - ny)
        v += 0.0001 * wall_pen if i_am_pursuer else -0.0001 * wall_pen

        if bestv is None or v > bestv:
            bestv = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
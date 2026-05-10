def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    gw, gh = observation.get("grid_width", 8), observation.get("grid_height", 8)

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    if not resources:
        # Deterministic center drift with obstacle avoidance
        tx, ty = gw // 2, gh // 2
        best = [0, 0]
        bestv = 10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if (dx == 0 and dy == 0) or (in_bounds(nx, ny) and (nx, ny) not in obstacles):
                    v = abs(tx - nx) + abs(ty - ny)
                    if v < bestv:
                        bestv = v
                        best = [dx, dy]
        return best

    # Pick target resource we can win (or at least improve relative position).
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = abs(rx - sx) + abs(ry - sy)
        opd = abs(rx - ox) + abs(ry - oy)
        lead = opd - myd  # positive => we are closer than opponent
        # If any winnable, prioritize most winnable; otherwise block opponent by maximizing lead and then urgency.
        key = (0 if lead < 0 else 1, lead, -myd, -(rx * 9 + ry))
        if best_key is None or key > best_key:
            best_key, best_r = key, (rx, ry)

    rx, ry = best_r

    # One-step lookahead: minimize our distance to target; also try to maximize our advantage.
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx == 0 and dy == 0) or (in_bounds(nx, ny) and (nx, ny) not in obstacles):
                myd2 = abs(rx - nx) + abs(ry - ny)
                opd2 = abs(rx - ox) + abs(ry - oy)
                # Secondary: prefer moves that increase our relative lead after the step,
                # and discourage stepping into opponent's nearest-resource region by keeping myd2 small.
                rel = opd2 - myd2
                score = (-(0 if myd2 == 0 else 1), rel, -myd2, -((nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)))
                if best_score is None or score > best_score:
                    best_score = score
                    best_move = [dx, dy]
    return best_move
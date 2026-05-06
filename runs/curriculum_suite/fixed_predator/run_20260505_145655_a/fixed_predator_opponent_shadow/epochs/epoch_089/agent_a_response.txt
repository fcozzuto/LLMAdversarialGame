def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Candidate moves (deterministic order)
    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            moves.append((dx, dy))

    def target_value(px, py):
        best = None
        best_tv = None
        best_dopp = None
        for rx, ry in resources:
            d_me = abs(rx - px) + abs(ry - py)
            d_opp = abs(rx - ox) + abs(ry - oy)
            # Prefer resources where we are closer than opponent; penalize long travel.
            tv = (d_opp - d_me) * 1000 - d_me + (0.001 * d_opp)
            if best_tv is None or tv > best_tv:
                best, best_tv, best_dopp = (rx, ry), tv, d_opp
            elif tv == best_tv:
                # Tie-break toward closer opponent distance and then lexicographically.
                if d_opp < best_dopp or ((d_opp == best_dopp) and (rx, ry) < best):
                    best, best_tv, best_dopp = (rx, ry), tv, d_opp
        return best_tv, best

    best_move = (0, 0)
    best_score = None
    best_tgt = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or cell_blocked(nx, ny):
            continue
        tv, tgt = target_value(nx, ny)
        if tv is None:
            continue
        # Slightly discourage moving away from current best target once decided.
        if best_tgt is not None and tgt == best_tgt:
            tv2 = tv + 0.5
        else:
            tv2 = tv
        # Small tie-break: prefer decreasing manhattan distance to target.
        if best_score is None or tv2 > best_score:
            best_score = tv2
            best_move = (dx, dy)
            best_tgt = tgt
        elif tv2 == best_score:
            # deterministic tie-break by direction lexicographic
            if (dx, dy) < best_move:
                best_move = (dx, dy)
                best_tgt = tgt

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # No resources: move to intercept opponent direction
    if not resources:
        dx, dy = -sign(ox - x), -sign(oy - y)
        return [dx, dy]

    # Evaluate a resource target from a given position
    def res_value(tx, ty, px, py):
        d_me = abs(tx - px) + abs(ty - py)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Prefer targets we are closer to; also prefer closer overall.
        return (d_opp - d_me) * 1000 - d_me

    # Choose the best target deterministically
    best_t = None
    best_tv = None
    for r in resources:
        tx, ty = r[0], r[1]
        tv = res_value(tx, ty, x, y)
        key = (tv, -abs(tx - ox) - abs(ty - oy), -tx - ty)  # deterministic tie-break
        if best_tv is None or key > best_tv:
            best_tv = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Among legal moves, pick the one that maximizes improvement toward the chosen target
    best_move = (0, 0)
    best_score = None
    cur_d = abs(tx - x) + abs(ty - y)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or cell_blocked(nx, ny):
            continue
        d_new = abs(tx - nx) + abs(ty - ny)
        # Strongly prefer getting closer; slightly prefer also moving away from opponent when tied.
        score = (cur_d - d_new) * 10000 - d_new + (abs(tx - ox) + abs(ty - oy)) * 0.001
        # Deterministic tie-break: prefer horizontal/vertical progress, then lexicographic.
        score_key = (score, -abs(ox - nx) - abs(oy - ny), -dx - dy, dx, dy)
        if best_score is None or score_key > best_score:
            best_score = score_key
            best_move = (dx, dy)

    # If all moves blocked by obstacles, stay
    return [int(best_move[0]), int(best_move[1])]
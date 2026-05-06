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

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda d: (d[0], d[1]))

    # Precompute for each target: lead = opp closer? and distance
    # Prefer targets that are closer to us than opponent (large positive lead, penalize own distance).
    def target_score(tx, ty, cx, cy):
        d_me = abs(tx - cx) + abs(ty - cy)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me
        return lead * 1000 - d_me + 0.01 * d_opp

    best_move = (0, 0)
    best_val = None

    # One-step lookahead: after moving, pick best reachable resource and evaluate.
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            nx, ny = x, y  # engine would keep us, but treat consistently
        # Find best target from current post-move position (deterministic tie-break)
        tv = None
        for r in resources:
            tx, ty = r[0], r[1]
            val = target_score(tx, ty, nx, ny)
            if tv is None or val > tv or (val == tv and (tx, ty) < best_t):
                tv = val
                best_t = (tx, ty)
        # Additional term: prefer moves that get closer to the chosen target and keep/extend lead
        tx, ty = best_t
        move_dist = abs(tx - nx) + abs(ty - ny)
        opp_dist = abs(tx - ox) + abs(ty - oy)
        # If equal value, deterministically prefer smallest move_dist, then lexicographic dx,dy
        cand = (tv, -move_dist, opp_dist, -dx, -dy)
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
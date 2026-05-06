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

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best = None
    best_tv = None
    for tx, ty in resources:
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Prefer resources where we are closer (or opponent farther), but keep progress cost-aware.
        tv = (d_opp - d_me) * 1000 - d_me + 0.001 * d_opp
        if best_tv is None or tv > best_tv or (tv == best_tv and (d_opp < (abs(best[0] - x) + abs(best[1] - y)) if best else True)):
            best_tv = tv
            best = (tx, ty)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_me = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        adv = (d_opp - d_me) * 1000 - d_me
        # Small deterministic tiebreakers to avoid oscillations and favor staying safe.
        dist_op = abs(nx - ox) + abs(ny - oy)
        dist_me_now = abs(tx - x) + abs(ty - y)
        progress = dist_me_now - d_me
        score = adv + 2 * progress - 0.01 * dist_op - 0.0001 * (nx * 31 + ny * 17)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
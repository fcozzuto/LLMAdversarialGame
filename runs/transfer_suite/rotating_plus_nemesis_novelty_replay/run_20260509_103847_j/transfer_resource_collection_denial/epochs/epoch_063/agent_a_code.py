def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target: maximize advantage; boost resources aligned with opponent (likely sweep path).
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds
        line = (rx == ox) or (ry == oy)
        # Deterministic: higher is better for score, then closer to us.
        cand_score = adv + (2 if line else 0)
        key = (-cand_score, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = man(nx, ny, tx, ty)
        # Keep/restore advantage against opponent for the chosen target.
        do2 = man(ox, oy, tx, ty)
        cur_adv = do2 - ds2
        # Prefer maximizing advantage, then minimizing distance, then deterministic.
        move_key = (-cur_adv, ds2, dx, dy, nx, ny)
        if best_move is None or move_key < best_move[0]:
            best_move = (move_key, (dx, dy))

    if best_move is None:
        # If all moves blocked, stay.
        return [0, 0]
    return [int(best_move[1][0]), int(best_move[1][1])]
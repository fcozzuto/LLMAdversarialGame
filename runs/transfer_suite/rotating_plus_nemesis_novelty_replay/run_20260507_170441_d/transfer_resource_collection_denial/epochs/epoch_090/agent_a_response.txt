def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = observation.get("turns_remaining", 0)

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def dist8(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    if not resources:
        return [0, 0]

    best = None
    best_val = -10**18
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        # Prefer resources we can secure: earlier arrival than opponent, or still feasible.
        time_feasible = 1.0 if (turns_remaining == 0 or my_d <= turns_remaining) else 0.0
        adv = op_d - my_d
        secure_bonus = 900.0 if adv > 0 else (-200.0 if adv < 0 else 0.0)
        soon_pen = my_d * 5.0 + (0.5 * max(0, my_d - turns_remaining)) if turns_remaining else my_d * 5.0
        center_bias = (abs((w - 1) / 2 - rx) + abs((h - 1) / 2 - ry)) * 0.05
        val = (secure_bonus + adv * 110.0 + 200.0 * time_feasible) - soon_pen - center_bias
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_t = dist8(nx, ny, tx, ty)
        d_to_op = dist8(nx, ny, ox, oy)
        # Greedy toward target; small pressure to avoid letting opponent close too fast.
        score = -d_to_t * 10.0 + d_to_op * 0.1
        # Deterministic tie-break: lexicographically smallest (dx,dy)
        if score > best_score or (score == best_score and (dx, dy) < best_m):
            best_score = score
            best_m = (dx, dy)
    return [best_m[0], best_m[1]]
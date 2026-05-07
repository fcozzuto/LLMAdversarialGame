def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Pick target that we are closest to relative to opponent (maximize opp_dist - self_dist)
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (od - sd, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"]:
            if (nx, ny) not in obstacles:
                valid.append((dx, dy, nx, ny))

    def step_eval(nx, ny):
        self_d = man(nx, ny, tx, ty)
        opp_d = man(nx, ny, ox, oy)
        # Primary: get closer to our target; Secondary: avoid giving opponent immediate proximity to that target
        # Tertiary: reduce opponent's distance advantage
        opp_target_d_after = man(nx, ny, tx, ty)  # same cell, but keeps scale deterministic
        # Score higher is better
        return (-self_d, opp_d, -opp_target_d_after, nx, ny)

    best_move = None
    best_score = None
    # If target is adjacent, prioritize taking it immediately; else, greedily approach while not stepping into traps
    for dx, dy, nx, ny in valid:
        if (nx, ny) == (tx, ty):
            return [dx, dy]
        sc = step_eval(nx, ny)
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return list(best_move) if best_move is not None else [0, 0]
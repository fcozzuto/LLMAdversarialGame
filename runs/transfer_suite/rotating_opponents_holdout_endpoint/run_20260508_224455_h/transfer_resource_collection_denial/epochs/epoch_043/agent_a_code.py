def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Pick best resource by who can arrive first; tie-break by smaller our distance.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources where we are not later (ds<=do). Otherwise minimize lateness.
        if ds <= do:
            key = (0, do - ds, ds, rx, ry)  # win earlier by larger margin
        else:
            key = (1, ds - do, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Candidate moves with basic obstacle avoidance.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (10**9, 0, 0)
    w = observation["grid_width"]; h = observation["grid_height"]

    # When we can win soon, be greedy; otherwise bias toward blocking cells near target's line.
    # (Small, deterministic shaping; no global search.)
    urgent = 1 if man(sx, sy, tx, ty) <= 3 else 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_self = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)

        # Shaping: prefer reducing distance to target, but also avoid stepping where opponent is much closer.
        # Also slightly prefer staying on same row/col if opponent likely sweeps rows.
        sweep_bias = 0
        if urgent:
            sweep_bias = -1 if (ny == sy and dx != 0) else 0
        else:
            sweep_bias = -1 if (nx == sx and dy != 0) else 0

        our_adv = d_self - man(ox, oy, tx, ty)
        opp_threat = (man(ox, oy, nx, ny) - d_self)

        # Lower is better
        key = (d_self, -d_opp, our_adv, opp_threat, sweep_bias, dx, dy)
        if key < best_move:
            best_move = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]
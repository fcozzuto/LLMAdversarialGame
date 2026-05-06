def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # "Interference": focus on the resource where opponent has the biggest advantage,
    # and try to match that advantage (or at least reduce it).
    best_res = None
    best_gap = -10**9
    for rx, ry in resources:
        my_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        gap = opp_d - my_d  # positive means opponent farther? actually opp_d - my_d
        # We want opponent to be closer => my_d - opp_d is positive, so opp_d - my_d is negative.
        # Choose most negative (largest opponent advantage in being closer).
        if best_res is None or gap < best_gap:
            best_gap = gap
            best_res = (rx, ry)

    tx, ty = best_res

    # Secondary target: our nearest resource to avoid drifting too far.
    near_rx, near_ry = min(resources, key=lambda p: man(sx, sy, p[0], p[1]))

    cur_my_target = man(sx, sy, tx, ty)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_d_t = man(nx, ny, tx, ty)
        opp_d_t = man(ox, oy, tx, ty)
        # Try to reduce the opponent's closeness advantage at the contested resource.
        # If opponent is closer, opp_d_t < my_d_t, so my_d_t - opp_d_t is positive; minimize it.
        contest = my_d_t - opp_d_t

        # Also keep moving forward on overall value: reduce distance to our nearest resource slightly.
        my_d_near = man(nx, ny, near_rx, near_ry)

        # Prefer moves that reduce distance to the contested target (deterministic directional push).
        delta_to_target = cur_my_target - my_d_t

        # Gentle anti-stall: discourage staying if it doesn't improve contested/near.
        stall_pen = 0 if (dx != 0 or dy != 0) else 0.25

        # Higher is better.
        score = (-contest) * 5 + delta_to_target * 2 + (-my_d_near) * 0.15 - stall_pen

        key = (-score, dx, dy, my_d_t, my_d_near)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]
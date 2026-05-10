def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role") or "")
    evader = "evader" in role.lower()

    dlist = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    cur_to_opp_x = ox - sx
    cur_to_opp_y = oy - sy

    # If opponent is near a wall, bias to keep pressure along that axis (more "interception" vs simple chasing).
    wall_bias_x = 0
    if ox <= 1:
        wall_bias_x = 1
    elif ox >= w - 2:
        wall_bias_x = -1
    wall_bias_y = 0
    if oy <= 1:
        wall_bias_y = 1
    elif oy >= h - 2:
        wall_bias_y = -1

    best = None
    best_sc = None

    for dx, dy in dlist:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        ddx = nx - ox
        ddy = ny - oy
        man2 = ddx * ddx + ddy * ddy

        # Avoid stepping into obstacles' immediate neighborhood to reduce "wall runner" traps.
        neigh_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in blocked:
                    neigh_pen += 0.35

        # Interception bias: if we can move to reduce separation along the dominant direction.
        step_dir_x = 0 if cur_to_opp_x == 0 else (1 if cur_to_opp_x > 0 else -1)
        step_dir_y = 0 if cur_to_opp_y == 0 else (1 if cur_to_opp_y > 0 else -1)
        align_bonus = 0
        if not evader:
            if dx == step_dir_x:
                align_bonus += 0.25
            if dy == step_dir_y:
                align_bonus += 0.25
            if dx == 0 and dy == 0:
                align_bonus -= 0.2
            align_bonus += 0.15 * wall_bias_x * dx + 0.15 * wall_bias_y * dy
        else:
            # For evader, bias toward increasing separation and sliding along walls opposite the pursuer.
            align_bonus += 0.12 * (-wall_bias_x) * dx + 0.12 * (-wall_bias_y) * dy
            if dx == 0 and dy == 0:
                align_bonus -= 0.2

        # Add slight preference for diagonal progress (breaks symmetric oscillations deterministically).
        diag_pref = 0.08 if (dx != 0 and dy != 0) else 0.0

        # Final score: pursuer minimizes distance, evader maximizes distance.
        if evader:
            sc = man2 + align_bonus + diag_pref - neigh_pen
        else:
            sc = -man2 + align_bonus + diag_pref - neigh_pen

        if best_sc is None or (sc > best_sc):
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
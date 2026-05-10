def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if is_evader:
        # Prefer maximizing distance while also heading to the farthest corner (helps against corner evasion bots).
        far_corner = None
        far_d2 = -1
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            dx, dy = cx - ox, cy - oy
            d2 = dx * dx + dy * dy
            if d2 > far_d2:
                far_d2, far_corner = d2, (cx, cy)
        tx, ty = far_corner if far_corner is not None else corners[0]
    else:
        tx, ty = ox, oy

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        dpx, dpy = nx - ox, ny - oy
        d2 = dpx * dpx + dpy * dpy
        if is_evader:
            # Move away from pursuer; slight pull toward target corner.
            tcx, tcy = tx, ty
            # Penalize getting closer: primary is distance increase relative to current.
            curx, cury = sx - ox, sy - oy
            cur_d2 = curx * curx + cury * cury
            dist_gain = d2 - cur_d2
            tdx, tdy = nx - tcx, ny - tcy
            tcurx, tcury = sx - tcx, sy - tcy
            t_d2 = tdx * tdx + tdy * tdy
            tcur_d2 = tcurx * tcurx + tcury * tcury
            corner_gain = tcur_d2 - t_d2
            score = 1000.0 * dist_gain + 1.0 * corner_gain
        else:
            # Move toward pursuer/opponent position; avoid corner traps by preferring lines that reduce distance most.
            dist_to_target = d2
            # Small bias: prefer reducing both axes (diagonal progress) when tied.
            axis_bias = -(abs(nx - ox) + abs(ny - oy))
            score = -dist_to_target * 10.0 + axis_bias

        if best_score is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if not isinstance(best, tuple):
        best = (0, 0)
    dx, dy = best
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        dx, dy = 0, 0
    return [int(dx), int(dy)]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "seeker"))
    if not is_evader and not is_pursuer:
        is_evader = False  # default to pursuer behavior if unclear

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    obstacles_list = list(obs)
    def obst_pen(nx, ny):
        # small penalty if stepping near obstacles (helps avoid deadlocks)
        if not obstacles_list:
            return 0
        m = 10**9
        for (bx, by) in obstacles_list:
            d = (nx - bx) * (nx - bx) + (ny - by) * (ny - by)
            if d < m:
                m = d
        return -1 if m <= 1 else (0 if m <= 4 else 0)

    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dxx, dyy = nx - ox, ny - oy
        dist2 = dxx * dxx + dyy * dyy
        if is_evader:
            # evade: maximize distance; bias toward farthest corner; prefer moves that don't get closer in both axes
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_bias = abs(far_corner[0] - nx) + abs(far_corner[1] - ny)
            closer_axes = (abs(dxx) < abs(sx - ox) and abs(dyy) < abs(sy - oy))
            val = dist2 * 100 + corner_bias * 2 + (0 if not closer_axes else -500) + obst_pen(nx, ny)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            # pursue: minimize distance; strong preference for moving along the reducing direction even if diagonal
            val = dist2 * 100 + obst_pen(nx, ny)
            # tie-break: choose move that makes dx and dy changes consistent with closing
            sgnx = 0 if (nx == ox) else (1 if nx > ox else -1)
            sgny = 0 if (ny == oy) else (1 if ny > oy else -1)
            dir_bonus = 0
            if (sx - ox) != 0 and sgnx == (1 if (sx - ox) < 0 else -1):
                dir_bonus -= 3
            if (sy - oy) != 0 and sgny == (1 if (sy - oy) < 0 else -1):
                dir_bonus -= 3
            val = val + dir_bonus
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
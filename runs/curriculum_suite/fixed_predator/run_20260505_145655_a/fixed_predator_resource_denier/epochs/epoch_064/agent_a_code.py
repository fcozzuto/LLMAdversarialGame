def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        deny = od - sd
        center_bias = -(((rx - cx0) ** 2 + (ry - cy0) ** 2) * 1e-4)
        t = (deny * 10 - sd + center_bias, -od, sd, rx, ry)
        if best is None or t > best:
            best = t
    tx, ty = best[3], best[4]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    curr_sd = man(sx, sy, tx, ty)
    curr_od = man(ox, oy, tx, ty)

    best_m = None
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)  # opponent position unchanged this turn

        # Primary: increase denial (keep/extend advantage); Secondary: reduce own distance.
        # Tertiary: nudge toward center to avoid being stuck.
        denial_score = (od - sd)
        delta_own = curr_sd - sd
        center_bias = -(((nx - cx0) ** 2 + (ny - cy0) ** 2) * 1e-4)

        # Slightly prefer moves that bring us closer than the opponent is to the target.
        opp_close = 0
        if od > 0:
            opp_close = -1e-3 * (sd / (od + 1.0))

        s = denial_score * 20 + delta_own * 5 - sd * 0.6 + center_bias + opp_close
        if best_s is None or s > best_s:
            best_s = s
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]
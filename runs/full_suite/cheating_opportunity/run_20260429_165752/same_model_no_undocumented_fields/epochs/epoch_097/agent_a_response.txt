def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (sx, sy) in obstacles:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    my = (sx, sy)
    opp = (ox, oy)

    if resources:
        my_target = min(resources, key=lambda r: (cheb(my, r), r[0], r[1]))
        opp_target = min(resources, key=lambda r: (cheb(opp, r), r[0], r[1]))
    else:
        my_target = (w // 2, h // 2)
        opp_target = my_target

    opp_dist_before = cheb(opp, opp_target)
    best = None
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nm = (nx, ny)

        my_gain = opp_gain = 0
        my_dist = cheb(nm, my_target)
        opp_dist_after = opp_dist_before  # we can't move opponent; estimate "blocking" via proximity to opponent
        opp_gain = -cheb(nm, opp)  # being closer to opponent can disrupt routing in many engines

        # obstacle proximity penalty (prefer open space)
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    near_obs += 1

        # Choose move that reduces our distance while also improving "blocking"/space control
        val = (opp_dist_after - opp_dist_before) + (opp_gain) - 0.7 * near_obs - 0.4 * my_dist

        # Deterministic tie-break
        tie = (nx, ny)
        if best is None or val > best_val or (val == best_val and tie < best):
            best_val = val
            best = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])] if best is not None else [0, 0]
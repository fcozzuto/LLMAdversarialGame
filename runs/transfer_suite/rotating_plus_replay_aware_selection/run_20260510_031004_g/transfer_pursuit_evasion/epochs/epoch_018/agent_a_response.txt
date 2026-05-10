def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in self_role
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corner = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
    if evader:
        target = max(corner, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        target = (w - 1 - ox, h - 1 - oy)

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def dist_to_target2(x, y):
        tx, ty = target
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def free_count(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                cnt += 1
        return cnt

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue

        d2 = dist2(nx, ny)
        t2 = dist_to_target2(nx, ny)
        mob = free_count(nx, ny)

        # obstacle danger: prefer moving away if near obstacles
        danger = 0
        for ax, ay in obs_set:
            ddx, ddy = nx - ax, ny - ay
            danger += 1.0 / (1 + ddx * ddx + ddy * ddy)

        if evader:
            # maximize distance from pursuer, also head toward far corner and keep mobility
            val = (d2 * 1.0) + (t2 * -0.02) + (mob * 0.15) - (danger * 0.25)
        else:
            # minimize distance to evader, maintain mobility and move toward intercepted target
            val = (-d2 * 1.0) + (t2 * -0.02) + (mob * 0.08) - (danger * 0.15)

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]
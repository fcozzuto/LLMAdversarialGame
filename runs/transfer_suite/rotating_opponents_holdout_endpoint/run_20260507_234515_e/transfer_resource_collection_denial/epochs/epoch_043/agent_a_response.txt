def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0: d1 = -d1
        d2 = ay - by
        if d2 < 0: d2 = -d2
        return d1 if d1 >= d2 else d2

    def obstacle_pen(nx, ny):
        pen = 0
        for ax, ay in obstacles:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                pen += 2
            if ax == nx and ay == ny:
                pen += 10
        return pen

    tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
    if not resources:
        best = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dist_mid = abs(nx - tx) + abs(ny - ty)
            opp_dist = cheb(nx, ny, ox, oy)
            key = (dist_mid + obstacle_pen(nx, ny) - 0.3 * opp_dist, opp_dist, dist_mid)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    best = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_res_key = None
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obs:
                continue
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # Prefer moves that reduce self distance to resources more than opponent; avoid traps near obstacles.
            k = (self_d - 0.85 * opp_d, self_d, -cheb(nx, ny, ox, oy))
            if best_res_key is None or k < best_res_key:
                best_res_key = k
        # Combine best resource attraction with local safety.
        local_key = (best_res_key[0] + obstacle_pen(nx, ny), best_res_key[1], best_res_key[2])
        if best_key is None or local_key < best_key:
            best_key = local_key
            best = (dx, dy)

    return [best[0], best[1]]
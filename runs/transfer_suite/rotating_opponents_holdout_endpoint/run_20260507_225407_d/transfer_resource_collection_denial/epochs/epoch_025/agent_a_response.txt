def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Prefer resources where we are closer (or can become closer next move)
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - myd  # positive means we are ahead
        key = (adv, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        best_r = resources[0]
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Score each move by how much it improves our lead to the chosen target; tie-break with safety.
    best_m = None
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= gw or ny >= gh:
            continue
        if (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        lead_after = od - myd
        # Prefer moves that also reduce distance to any remaining resource if lead is similar.
        min_res_d = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            d = cheb(nx, ny, rx, ry)
            if min_res_d is None or d < min_res_d:
                min_res_d = d
        if min_res_d is None:
            min_res_d = 0
        # Avoid getting too close to obstacles neighborhood (simple deterministic penalty).
        neigh_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                cx, cy = nx + ax, ny + ay
                if (cx, cy) in obs:
                    neigh_pen += 1
        key = (lead_after, -min_res_d, -neigh_pen, dx, dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [best_m[0], best_m[1]]
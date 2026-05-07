def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if not p or len(p) < 2:
            continue
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    res_pts = []
    for r in resources:
        if not r or len(r) < 2:
            continue
        try:
            x, y = int(r[0]), int(r[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            res_pts.append((x, y))

    neigh = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not res_pts:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            return [dx, dy]
        for dx, dy in neigh:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        adx = ax - bx
        ady = ay - by
        return abs(adx) if abs(adx) > abs(ady) else abs(ady)  # Chebyshev

    best_move = [0, 0]
    best_val = -10**18

    # Deterministically pick: best "lead" to a resource based on our next position.
    # Primary: minimize our distance to chosen resource minus opponent distance (maximize lead).
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
            continue
        best_for_move = -10**18
        for rx, ry in res_pts:
            d_me = dist((nx, ny), (rx, ry))
            d_op = dist((ox, oy), (rx, ry))
            # More advantage is better; small tie-break favors closer absolute approach.
            val = (d_op - d_me) * 1000 - d_me
            if val > best_for_move:
                best_for_move = val
        if best_for_move > best_val:
            best_val = best_for_move
            best_move = [dx, dy]

    return best_move
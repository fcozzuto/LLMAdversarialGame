def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    dxdy = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    self_is_evader = ("evader" in roles) and ("purs" not in roles)

    def dist2(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def best_corner_point(points):
        # deterministic min by (dist2, x, y)
        best = None
        bx, by = 0, 0
        for x, y in points:
            d = dist2((ox, oy), (x, y))
            cand = (d, x, y)
            if best is None or cand < best:
                best = cand
                bx, by = x, y
        return bx, by

    if self_is_evader:
        # Run toward the farthest corner from the pursuer position (ox,oy).
        target = None
        best = None
        for cx, cy in corners:
            d = dist2((sx, sy), (cx, cy)) - 2 * dist2((ox, oy), (cx, cy))
            cand = (-d, cx, cy)
            if best is None or cand < best:
                best = cand
                target = (cx, cy)
        tx, ty = target
    else:
        # If opponent is near a corner, deny it by heading toward that corner.
        cx, cy = best_corner_point(corners)

        # Also slightly bias to reduce distance, so not purely corner-chasing.
        tx, ty = cx, cy

    best_move = (0, 0)
    best_score = None

    for dx, dy in dxdy:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        if self_is_evader:
            # maximize distance from opponent and move toward chosen corner target
            score = dist2((nx, ny), (ox, oy)) + 0.1 * (-dist2((nx, ny), (tx, ty)))
        else:
            # minimize distance to opponent, and strongly move toward target corner (deny)
            score = -dist2((nx, ny), (ox, oy)) + 0.5 * (-dist2((nx, ny), (tx, ty)))

        cand = (-(score), dx, dy)  # deterministic min
        if best_score is None or cand < best_score:
            best_score = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
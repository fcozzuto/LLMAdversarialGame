def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Select resource that maximizes current advantage (deny-minded), then move to improve it.
    def best_resource_for(x, y):
        best = None
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            cap = 1 if (x, y) == (rx, ry) else 0
            # Prefer immediate capture, then better advantage, then closer to opponent's best.
            key = (cap, adv, -ds, -(rx * 8 + ry))
            if best is None or key > best:
                best = (rx, ry, ds, do, adv, cap)
        return best

    # Evaluate moves with obstacle avoidance; if blocked/out-of-bounds, assume staying.
    best_move = [0, 0]
    best_key = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            nx, ny = sx, sy  # engine would keep in place
        brx, bry, ds, do, adv, cap = best_resource_for(nx, ny)
        # Encourage getting strictly closer to that resource, and maintaining/creating advantage.
        d_after = cheb(nx, ny, brx, bry)
        d_now = cheb(sx, sy, brx, bry)
        improve = d_now - d_after
        # Secondary tie-break: keep distance to opponent moderate (avoid being chased into bad trades).
        oppd = cheb(nx, ny, ox, oy)
        key = (cap, adv, improve, -d_after, -oppd, -(brx * 8 + bry), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move
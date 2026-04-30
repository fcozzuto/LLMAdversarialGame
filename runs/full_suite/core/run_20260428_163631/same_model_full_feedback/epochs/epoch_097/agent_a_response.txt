def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    if not resources:
        return [0, 0]

    if (sx, sy) in set(resources):
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Predict opponent contesting: assume opponent prefers resources closest to them.
    # Target the resource maximizing advantage: (opp_dist - self_dist), then self_dist, then closeness to center.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        center_bias = cheb(rx, ry, cx, cy)
        # Higher is better for first component; deterministic tie-breakers.
        key = (d_opp - d_self, -d_self, -center_bias, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose a move that reduces our distance to target, with obstacle avoidance.
    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            # Extra bias: keep away from opponent slightly while heading to target.
            do = cheb(nx, ny, ox, oy)
            val = (-d, do, -abs((nx - ox)) - abs((ny - oy)))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move
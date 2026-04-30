def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Fallback: move to increase distance from opponent deterministically
        dxs = (-1, 0, 1)
        best = None
        bestv = None
        for dx in dxs:
            for dy in dxs:
                nx, ny = sx + dx, sy + dy
                if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                    continue
                v = cheb(nx, ny, ox, oy)
                if bestv is None or v > bestv:
                    bestv = v
                    best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Choose target resource where we have (or can gain) an advantage
    best_r = None
    best_gain = None
    for r in resources:
        rx, ry = r[0], r[1]
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gain = (od - sd) * 10 - sd  # prioritize winning access; tie-break with closer
        if best_gain is None or gain > best_gain:
            best_gain = gain
            best_r = (rx, ry)

    tx, ty = best_r

    # Evaluate next moves: approach target while discouraging giving opponent better access
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))

    opp_dist = cheb(ox, oy, tx, ty)
    best_move = (0, 0)
    best_val = None
    for dx, dy, nx, ny in candidates:
        self_d = cheb(nx, ny, tx, ty)

        # If opponent is closer to the target, slightly prefer moves that increase our distance to opponent
        # (deterministic "interference avoidance").
        dist_to_opp = cheb(nx, ny, ox, oy)
        cur_dist_to_opp = cheb(sx, sy, ox, oy)
        dist_delta = dist_to_opp - cur_dist_to_opp

        val = -self_d * 4 + (dist_delta) * (1 if opp_dist <= cheb(sx, sy, tx, ty) else -0.5)
        # Tiny deterministic tie-break: favor staying close to grid center-ish
        val += -0.01 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
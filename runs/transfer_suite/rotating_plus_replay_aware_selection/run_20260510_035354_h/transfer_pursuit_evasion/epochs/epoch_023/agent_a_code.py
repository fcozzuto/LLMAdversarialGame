def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def role_is_purs(role):
        r = (role or "").lower()
        if "purs" in r:
            return True
        if "evad" in r:
            return False
        return None

    sr = role_is_purs(observation.get("self_role"))
    orr = role_is_purs(observation.get("opponent_role"))
    if sr is None:
        sr = (orr is False)
    i_am_pursuer = bool(sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    def obstacle_local_cost(x, y):
        # Higher if surrounded; discourages moving near obstacles
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    c += 1
        return c

    def edge_cost(x, y):
        # Discourage hugging walls a bit (helps vs zigzag drift)
        return min(x, y, w - 1 - x, h - 1 - y)

    # Deterministic tie-break order: fixed move iteration
    best_move = [0, 0]
    best_val = None

    tx, ty = ox, oy
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d = dist2(nx, ny, tx, ty)
        ocost = obstacle_local_cost(nx, ny)

        # Alignment bonus encourages directed motion rather than sideways zigzags
        ax = 0 if tx == sx else (1 if tx > sx else -1)
        ay = 0 if ty == sy else (1 if ty > sy else -1)
        align = abs(dx - ax) + abs(dy - ay)  # smaller is better when pursuing

        e = edge_cost(nx, ny)

        if i_am_pursuer:
            # Minimize: closer is better, also prefer cleaner corridors and directed pursuit
            val = d + 0.9 * ocost + 1.2 * align - 0.05 * e
            better = (best_val is None) or (val < best_val) or (val == best_val and (dx, dy) < (best_move[0], best_move[1]))
        else:
            # Evader: maximize distance; avoid obstacles and walls
            val = d - 1.0 * ocost + 0.2 * align + 0.35 * e
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < (best_move[0], best_move[1]))

        if better:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    legal.sort()

    def cheb(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x if x > y else y

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = min(legal, key=lambda m: cheb(sx + m[0], sy + m[1], cx, cy))
        return [best[0], best[1]]

    # Predict opponent's nearest resource and choose an action that maximizes either:
    # (1) our chance to beat them to a contested resource,
    # (2) otherwise, deny by moving orthogonally to their approach while progressing.
    opp_target = min(resources, key=lambda r: cheb(ox, oy, r[0], r[1]))
    tx, ty = opp_target

    best_move = legal[0]
    best_val = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Contested-resource value: maximize (opponent margin) and break ties by closeness to that resource.
        local = 0
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd
            # Strongly prefer resources we can reach no slower than opponent; else still consider margin.
            local += (margin * 1000) - sd

        # Denial / safe collection disruption bias: move away from opponent's direct approach line.
        # Approximate "approach direction" from opponent to its nearest target.
        apx = 0 if tx == ox else (1 if tx > ox else -1)
        apy = 0 if ty == oy else (1 if ty > oy else -1)
        # Perpendicular step direction measure using dot product with approach.
        # Lower dot magnitude => more orthogonal => more disruptive.
        dot = (nx - ox) * apx + (ny - oy) * apy
        denial = -abs(dot)

        # Also avoid clustering too close behind their target to prevent easy grabs.
        end_bias = 0
        dt = cheb(nx, ny, tx, ty)
        end_bias = -dt

        val = local + 50 * denial + 10 * end_bias
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
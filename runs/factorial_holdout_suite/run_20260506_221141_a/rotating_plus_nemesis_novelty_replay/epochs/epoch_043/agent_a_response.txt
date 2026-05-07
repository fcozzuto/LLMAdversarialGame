def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_ok(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs

    # Choose best immediate move based on improving race for contested resources,
    # with extra bias to resources on opponent's current row (sweep_rows).
    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not move_ok(nx, ny):
            continue

        # Evaluate the best resource we could "aim" at from the next position.
        best_resource_val = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            race = do - ds  # positive means we're closer (good)
            # sweep_rows bias: contest resources on opponent's current row
            row_bias = -abs(ry - oy)
            # slight preference for nearer resources after contesting
            dist_bias = -ds
            val = race * 1000 + row_bias * 10 + dist_bias
            if val > best_resource_val:
                best_resource_val = val

        # Prefer moves that reduce opponent's ability to contest us: keep race high.
        if best_resource_val > best_val:
            best_val = best_resource_val
            best = (dx, dy)

    if best == (0, 0):
        # fallback: move toward the closest resource in Chebyshev distance, avoiding obstacles
        target = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
        tx, ty = target
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        # ensure fallback move isn't blocked; if it is, try a simple alternative ordering
        cand = [(dx, dy), (dx, 0), (0, dy), (0, 0), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (-dx, -dy)]
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if move_ok(nx, ny):
                return [mx, my]
        return [0, 0]

    return [best[0], best[1]]
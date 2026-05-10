def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    # Choose a target resource: prefer those we can reach no later than opponent; otherwise least-bad delay.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if ds <= do:
            key = (0, -(do - ds), ds, rx, ry)  # win sooner by larger margin
        else:
            key = (1, ds - do, ds, rx, ry)     # minimize how late we are
        if best is None or key < best[0]:
            best = (key, rx, ry, ds, do)
    _, tx, ty, ds, do = best

    # If behind, aim for an intercept cell near the resource: step toward it a bit from our position.
    if ds <= do:
        gx, gy = tx, ty
    else:
        step = 1 if (do - ds) >= 2 else 0  # small anticipatory move; deterministic
        vx = 0 if tx == sx else (1 if tx > sx else -1)
        vy = 0 if ty == sy else (1 if ty > sy else -1)
        gx = clamp(sx + vx * max(0, 2 - step), 0, w - 1)
        gy = clamp(sy + vy * max(0, 2 - step), 0, h - 1)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx = sx + dx; ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            key = (1, 10**9, 10**9, 10**9)
        else:
            ns = man(nx, ny, gx, gy)
            no = man(ox, oy, tx, ty)  # keep pressure on same target
            adv = (no - ns)
            # Prefer shorter to goal, then larger advantage, then deterministic tie-break by dx,dy
            key = (0, ns, -adv, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
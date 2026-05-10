def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    resources = observation.get("resources", []) or []
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        xa = a - c; xa = -xa if xa < 0 else xa
        ya = b - d; ya = -ya if ya < 0 else ya
        return xa + ya

    # Prefer resources where we have an advantage over opponent (smaller distance), and slightly avoid cells near obstacles.
    def cell_risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    r += 1
        return r

    best_target = None
    best_val = -10**9
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # adv: we want ds smaller than do; large negative ds helps us.
        adv = do - ds
        near = cell_risk(rx, ry)
        # tie-breaker: prefer nearer overall while maintaining advantage
        val = 5 * adv - ds - 2 * near
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if dx == 0 and dy == 0:
            step_pen = 0.2
        else:
            step_pen = 0.0

        cur_ds = md(nx, ny, tx, ty)
        cur_do = md(ox, oy, tx, ty)
        adv = cur_do - cur_ds
        # also consider not moving into bad obstacle-adjacent zones
        score = 5 * adv - cur_ds - 1.5 * cell_risk(nx, ny) - step_pen

        # If we are already closer than opponent to the target, bias toward finishing (reduce ds)
        if adv > 0:
            score += 1.5 * (-cur_ds)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
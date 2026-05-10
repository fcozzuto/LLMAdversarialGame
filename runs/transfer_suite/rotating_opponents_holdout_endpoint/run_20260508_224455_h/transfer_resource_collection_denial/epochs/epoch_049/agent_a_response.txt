def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy
    def near_obs(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    return 1
        return 0

    if not resources:
        return [0, 0]

    # Pick a target with strong "race" advantage and reasonable approach feasibility.
    best_target = None
    best_tkey = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Prefer tiles we can reach at least as fast; otherwise still race but lower priority.
        adv = do - ds  # positive => we're closer
        # Also prefer targets that are not deep "trap" near obstacles.
        trap = near_obs(rx, ry)
        key = (0 if adv >= 0 else 1, -adv, ds + 2 * trap, rx, ry)
        if best_tkey is None or key < best_tkey:
            best_tkey = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Evaluate next step with deterministic tie-breaking.
    best_move = (0, 0)
    best_mkey = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)

        # Greedy race score: reduce our distance; increase opponent's relative distance.
        # Add small penalties to avoid obstacle-adjacent cells (more stable paths).
        obstacle_pen = near_obs(nx, ny)
        my_step_cost = abs(dxm) + abs(dym)

        # Key: higher race => smaller key by using negatives; deterministic by sorting by coordinates.
        race = (do2 - ds2)
        key = (-race, ds2 + 2 * obstacle_pen, my_step_cost, nx, ny)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]
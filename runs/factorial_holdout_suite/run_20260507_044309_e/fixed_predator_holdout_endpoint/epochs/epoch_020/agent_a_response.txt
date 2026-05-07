def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Predict opponent's next move (resource_denier): go to the closest resource by their distance.
    def best_opp_target():
        bx, by = resources[0]
        bd = man(ox, oy, bx, by)
        for rx, ry in resources[1:]:
            d = man(ox, oy, rx, ry)
            if d < bd or (d == bd and (rx, ry) < (bx, by)):
                bd, bx, by = d, rx, ry
        return bx, by

    tx, ty = best_opp_target()
    # Opponent chooses a legal step that minimizes distance to (tx, ty).
    best_op = (0, 0)
    best_od = 10**9
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        if d < best_od or (d == best_od and (dx, dy) < best_op):
            best_od, best_op = d, (dx, dy)
    nox, noy = ox + best_op[0], oy + best_op[1]

    best_move = (0, 0)
    best_val = -10**18
    # Evaluate our move against the predicted opponent position.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(nox, noy, rx, ry)
            # Prefer resources where we are closer after opponent moves; also prefer nearer picks overall.
            gap = od - sd
            val = gap * 10 - sd
            if val > local_best:
                local_best = val

        # Small tie-break: also prefer not to move into "dead ends" (stay closer to any resource).
        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
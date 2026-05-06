def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # If no resources, head to center while avoiding obstacles
    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            v = dist2(nx, ny, tx, ty)
            # tie-break deterministic: prefer smaller dx, then dy
            key = (v, abs(dx) + abs(dy), dx, dy)
            if key < best:
                best = key
        return [best[2], best[3]] if best[0] != 10**9 else [0, 0]

    # Evaluate moves by which resource we can reach sooner than opponent, with obstacle-safe local decision
    best_key = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # For each resource, estimate advantage at our next position.
        # Higher advantage is better; also slightly prefer closing distance to any nearby resource.
        move_best_for_this = -10**18
        near_term = 10**18
        for rx, ry in resources:
            sd = dist2(nx, ny, rx, ry)
            od = dist2(ox, oy, rx, ry)
            # advantage: how much closer we are than opponent (in squared terms)
            adv = od - sd
            if adv > move_best_for_this:
                move_best_for_this = adv
            dmin = sd
            if dmin < near_term:
                near_term = dmin

        # Also consider opponent pressure: move that increases our minimal advantage is good,
        # tie-break by smaller distance to closest resource, then deterministic delta.
        key = (
            -move_best_for_this,  # want larger adv => smaller negative
            near_term,
            abs(dx) + abs(dy),
            dx,
            dy,
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
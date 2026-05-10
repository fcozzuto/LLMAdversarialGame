def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da if da > db else db

    # If no resources, drift toward center while staying deterministic
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return [dx if abs(tx - x) >= abs(ty - y) else 0, dy if abs(ty - y) > abs(tx - x) else 0]

    alpha = 0.35
    best_move = [0, 0]
    best_key = None

    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose the resource that best supports winning the race from this candidate move.
        # Score favors: opponent farther than us, but also penalizes our long reach time.
        move_best = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Higher is better
            val = (od - sd) - alpha * sd
            # Deterministic tie-break: prefer smaller sd, then larger od, then lower coords
            key = (-(val), sd, -od, rx, ry)
            if move_best is None or key < move_best:
                move_best = key

        if move_best is None:
            continue

        if best_key is None or move_best < best_key:
            best_key = move_best
            best_move = [dx0, dy0]

    return best_move
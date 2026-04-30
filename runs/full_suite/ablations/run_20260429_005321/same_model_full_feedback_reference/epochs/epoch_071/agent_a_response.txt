def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    d0o = d2(sx, sy, ox, oy)

    if resources:
        # Race-aware target: prefer resources where we gain relative speed vs opponent.
        best_t = resources[0]
        best_key = None
        for tx, ty in resources:
            my = d2(sx, sy, tx, ty)
            opp = d2(ox, oy, tx, ty)
            # Lower is better: my distance minus advantage we expect if we get there first.
            key = (my - 1.15 * opp, my, tx, ty)
            if best_key is None or key < best_key:
                best_key, best_t = key, (tx, ty)
        tx, ty = best_t
    else:
        # No visible resources: drift to center to reduce opponent control variance.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose move: strongly move toward target, discourage positions that let opponent close the gap too much.
    best_move = (0, 0)
    best_val = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue
        to_t = d2(nx, ny, tx, ty)
        my_opp_dist = d2(nx, ny, ox, oy)
        # Estimate opponent incentive: if we move near opponent, likely lose races.
        opp_close = d0o - my_opp_dist  # positive if we get closer to opponent
        # Minor preference for not stepping onto "resource-crowding": if opponent is already closer to target, avoid.
        my_after = to_t
        opp_now = d2(ox, oy, tx, ty)
        race_pen = 0.65 * max(0.0, (my_after - opp_now))
        val = (to_t, opp_close * 1.25 + race_pen * 0.9, abs((nx - tx)) + abs((ny - ty)), nx, ny)
        if best_val is None or val < best_val:
            best_val, best_move = val, (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]
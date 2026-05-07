def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate this move by picking the resource that maximizes our advantage.
        move_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            # Prefer large advantage; if tied, prefer smaller our distance; then smaller opponent distance.
            val = adv * 1000 - sd * 3 - od
            if val > move_best:
                move_best = val
        # Prefer moves with better move_best; tie-break by immediate staying closer to current best resource estimate.
        if move_best > best_val:
            best_val = move_best
            best_move = [dx, dy]
        elif move_best == best_val:
            # Deterministic tie-break: prefer smaller |dx|+|dy| (stay if equally good), then lexicographic.
            if abs(dx) + abs(dy) < abs(best_move[0]) + abs(best_move[1]) or (
                abs(dx) + abs(dy) == abs(best_move[0]) + abs(best_move[1]) and (dx, dy) < (best_move[0], best_move[1])
            ):
                best_move = [dx, dy]

    return best_move
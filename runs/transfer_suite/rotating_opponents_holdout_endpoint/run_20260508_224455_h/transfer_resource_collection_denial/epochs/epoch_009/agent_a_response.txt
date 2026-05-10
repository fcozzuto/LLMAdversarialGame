def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0), (1, 0),
             (-1, 1),  (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    # Pick target resource where we maximize being closer than opponent.
    best = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        adv = opd - myd  # positive => we are closer
        key = (-adv, myd, rx, ry)  # maximize adv; tie by smaller myd
        if best is None or key < best[0]:
            best = (key, rx, ry)

    tx, ty = best[1], best[2]

    # Greedy move: choose next cell that maximizes advantage after move.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        adv = opd - myd
        # Prefer larger advantage; then smaller distance to target; then deterministic tie.
        score = (-adv, myd, -dx, -dy, nx, ny)
        if best_move is None or score < best_move[0]:
            best_move = (score, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]
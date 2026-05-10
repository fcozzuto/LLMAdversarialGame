def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick a target that we can reach more easily than the opponent, favoring earlier access.
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # prioritize advantage, then our closeness, then lower y (tend to sweep pressure by advancing)
        key = (opd - myd, -(myd), -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Precompute second-best resource for slight "unsticking" if we block ourselves.
    second = None
    second_key = None
    for rx, ry in resources:
        if (rx, ry) == (tx, ty):
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - myd, -(myd), -ry)
        if second_key is None or key > second_key:
            second_key = key
            second = (rx, ry)

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        adv = opd2 - myd2

        # Small term toward second resource to avoid local traps without changing main objective.
        stab = 0
        if second is not None:
            rx2, ry2 = second
            stab = -(cheb(nx, ny, rx2, ry2))

        # Higher is better: dominate on advantage, then closer to target, then prefer advancing (lower y)
        val = (adv * 1000) + (-(myd2) * 10) + (stab) + (-ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move
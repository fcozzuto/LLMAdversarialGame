def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick the most contestable resource (we are closer than them, and overall swing is high)
    best_tx, best_ty = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        swing = opd - myd  # positive => we are closer
        key = (swing, -myd, -(abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)))
        if best_key is None or key > best_key:
            best_key = key
            best_tx, best_ty = rx, ry

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_delta = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        myd2 = man(nx, ny, best_tx, best_ty)
        opd2 = man(ox, oy, best_tx, best_ty)
        score = (opd2 - myd2) * 6 - myd2

        # If a resource is already at our next cell, prioritize it strongly
        if (nx, ny) in resources:
            score += 100000

        # Mildly prefer staying out of dead-ends near obstacles
        neigh_blocked = 0
        for ddx, ddy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            tx, ty = nx + ddx, ny + ddy
            if not inb(tx, ty) or (tx, ty) in obstacles:
                neigh_blocked += 1
        score -= neigh_blocked * 0.5

        if best_score is None or score > best_score:
            best_score = score
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]
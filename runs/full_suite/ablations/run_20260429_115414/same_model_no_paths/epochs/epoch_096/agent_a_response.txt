def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def passable(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # deterministic move preference: reduce dx difference then dy; stay allowed
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ox0, oy0 = ox, oy

    # Evaluate each possible move by best attainable target score (no full search)
    best_move = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue

        # If staying on move rejected by engine, it will keep position; we don't allow into obstacles/outside.
        # Choose best target using "race" advantage and closeness.
        best_target = None
        best_tscore = -(10**18)
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox0, oy0, rx, ry)
            # Prefer resources where I can arrive earlier (positive advantage),
            # otherwise prefer closer ones (to not fall behind).
            # Add small tie-break favoring higher opponent distance.
            tscore = (opd - myd) * 100 - myd + opd * 0.1
            # Prefer more central tie-break to reduce dithering
            tscore += -0.01 * (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
            if tscore > best_tscore:
                best_tscore = tscore
                best_target = (rx, ry)

        # Secondary: if equal target score, prefer moves that reduce my distance to that chosen target
        rx, ry = best_target
        myd_after = cheb(nx, ny, rx, ry)
        tiebreak = -myd_after - 0.001 * (abs(nx - ox0) + abs(ny - oy0))
        score = best_tscore + tiebreak
        if score > best_move[0]:
            best_move = (score, dx, dy)

    return [int(best_move[1]), int(best_move[2])]
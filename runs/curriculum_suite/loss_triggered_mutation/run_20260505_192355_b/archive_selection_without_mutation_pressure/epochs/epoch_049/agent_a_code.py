def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_gap = -10**9
    best_dist = 10**9
    best_move = (0, 0)

    # Evaluate each move by how much it improves our advantage over opponent toward the best target.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue

        local_best_gap = -10**9
        local_best_dist = 10**9
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            gap = d_opp - d_self
            if gap > local_best_gap or (gap == local_best_gap and d_self < local_best_dist):
                local_best_gap = gap
                local_best_dist = d_self

        if (local_best_gap > best_gap) or (local_best_gap == best_gap and local_best_dist < best_dist) or \
           (local_best_gap == best_gap and local_best_dist == best_dist and (dxm, dym) < best_move):
            best_gap = local_best_gap
            best_dist = local_best_dist
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]
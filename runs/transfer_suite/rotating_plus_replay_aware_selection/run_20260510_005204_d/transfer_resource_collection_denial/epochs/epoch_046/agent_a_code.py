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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    centerx = (w - 1) / 2.0
    centery = (h - 1) / 2.0

    def target_score(tx, ty):
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Try to be strictly faster; otherwise prefer still-reachable closer options.
        lead = opd - myd
        mid_pen = abs(tx - centerx) + abs(ty - centery)
        return (lead, -myd, -mid_pen, -(tx + 13 * ty))

    best_t = None
    best_k = None
    for rx, ry in resources:
        k = target_score(rx, ry)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (rx, ry)

    tx, ty = best_t
    best_move = [0, 0]
    best_mk = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate move by how much it improves our relative pickup speed to the target,
        # plus a small bias toward reducing distance to the target.
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        lead2 = opd2 - myd2
        mid_pen2 = abs(nx - centerx) + abs(ny - centery)
        mk = (lead2, -myd2, -mid_pen2, -(nx + 11 * ny))
        if best_mk is None or mk > best_mk:
            best_mk = mk
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
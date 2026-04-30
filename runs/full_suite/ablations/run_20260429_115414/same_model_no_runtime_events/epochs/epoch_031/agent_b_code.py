def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_ds = {}
    for tx, ty in resources:
        opp_ds[(tx, ty)] = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Evaluate by best contest: prefer resources we can beat and get to first.
        local_best = -10**18
        for tx, ty in resources:
            myd = cheb(nx, ny, tx, ty)
            opd = opp_ds[(tx, ty)]
            margin = opd - myd  # positive if we are closer than opponent
            # Encourage reducing both distance and (opponent distance - ours).
            val = 2.5 * margin - 0.15 * myd
            if (tx, ty) == (nx, ny):
                val = 10**9
            if val > local_best:
                local_best = val

        # If no positive margin exists, still prefer closest resource.
        # (local_best already favors margin; this stabilizes when all margins negative.)
        if local_best < -1e17:
            local_best = -10**9 - cheb(nx, ny, resources[0][0], resources[0][1])

        # Deterministic tie-break: keep earlier move in moves list by only updating on >
        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
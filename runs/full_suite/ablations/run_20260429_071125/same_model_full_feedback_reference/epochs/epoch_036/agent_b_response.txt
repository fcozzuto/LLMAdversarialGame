def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Prefer resources where we are closer than the opponent; otherwise take a resource that least helps them.
        tx, ty = resources[0]
        best = None
        for (rx, ry) in resources:
            myd = manh(sx, sy, rx, ry)
            opd = manh(ox, oy, rx, ry)
            lead = opd - myd  # positive if we are closer
            # Rank: maximize lead, then minimize our distance, then stable by coordinates
            score = (lead, -myd, -rx, -ry)
            if best is None or score > best:
                best = score
                tx, ty = rx, ry

        # If everyone looks equally reachable late, shift to "denial": target the closest resource to opponent and move to contest it.
        if best and best[0] <= 0:
            opp_t = resources[0]
            opp_best = None
            for (rx, ry) in resources:
                opd = manh(ox, oy, rx, ry)
                score = (-opd, rx, ry)
                if opp_best is None or score < opp_best:
                    opp_best = score
                    opp_t = (rx, ry)
            tx, ty = opp_t

    # Choose one-step move that improves our reach to target; break ties by increasing opponent distance.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = manh(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # Encourage blocking: if we reduce our distance without making opponent closer to the same target, it's good.
        val = (-(myd), (opd - myd), -(abs(nx - tx) + abs(ny - ty)), -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 10**9)
        best_mv = [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if (d, -d) < best:
                best = (d, -d)
                best_mv = [dx, dy]
        return best_mv

    # Target selection: prefer resources where we have a timing advantage over the opponent.
    best_r = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive => we are closer (in Chebyshev steps)
        # Prefer higher lead; if tied, prefer nearer resources; then deterministic tie-break by coordinates.
        val = (lead, -min(ds, do), -ds, -rx, -ry)
        if best_val is None or val > best_val:
            best_val = val
            best_r = (rx, ry)

    rx, ry = best_r
    # Move selection: greedy improvement toward target, while also denying opponent by making their distance larger.
    best_score = None
    best_mv = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = cheb(nx, ny, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        # Primary: reduce our distance; Secondary: increase opponent's relative slack (op_d - my_d).
        score = (-my_d, -(op_d - my_d), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_mv = [dx, dy]

    return [int(best_mv[0]), int(best_mv[1])]
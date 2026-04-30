def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: prefer smaller dx then dy in listed order.
    # (dirs already deterministic)

    if not resources:
        cx, cy = w // 2, h // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if d < bestd:
                bestd = d
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18

    # Evaluate each move by the best resource we can reach first (margin vs opponent).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # compute max margin over resources; tie-break by larger margin then smaller self distance then lexicographic resource
        best_margin = -10**9
        best_self_d = 10**9
        best_rx, best_ry = 0, 0
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd
            if (margin > best_margin or
                (margin == best_margin and (sd < best_self_d or (sd == best_self_d and (rx < best_rx or (rx == best_rx and ry < best_ry)))))):
                best_margin = margin
                best_self_d = sd
                best_rx, best_ry = rx, ry

        # Penalize moves that do not improve our capture chances; slight preference toward being closer overall.
        # If best_margin is negative, still choose smallest self distance (keeping earlier strategy distinct).
        val = best_margin * 1000 - best_self_d
        if (val > best_val or (val == best_val and (dx < best_move[0] or (dx == best_move[0] and dy < best_move[1])))):
            best_val = val
            best_move = [dx, dy]

    return best_move
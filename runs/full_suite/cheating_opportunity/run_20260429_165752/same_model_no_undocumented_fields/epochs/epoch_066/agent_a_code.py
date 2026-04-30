def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not free(sx, sy):
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bestd, bestm = 10**9, (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < bestd:
                bestd, bestm = d, (dx, dy)
        return [bestm[0], bestm[1]]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Choose resource we are relatively closer to than opponent
    best_score, target = -10**18, resources[0]
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        center_bias = -0.02 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
        score = (od - myd) * 1.2 + center_bias - myd * 0.05
        if score > best_score:
            best_score, target = score, (rx, ry)

    rx, ry = target
    # Move greedily to reduce distance to target; deterministic tie-break favors diagonals and staying safe
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        myd = md(nx, ny, rx, ry)
        # Secondary criterion: also reduce opponent's distance to target (block when possible)
        od = md(ox, oy, rx, ry)
        block = md(ox, oy, rx, ry) - od  # always 0 here; keep structure cheap/deterministic
        # Tertiary: prefer diagonal moves when distances tie
        diag = 1 if dx != 0 and dy != 0 else 0
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (myd, stay_pen, -diag, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1 + 0) // 2, (h - 1 + 0) // 2
        best_dx = 0
        best_dy = 0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and cheb(nx, ny, tx, ty) <= cheb(sx, sy, tx, ty):
                best_dx, best_dy = dx, dy
                break
        return [best_dx, best_dy]

    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - ds) * 1000 - ds
        if (rx, ry) == (sx, sy):
            score += 10**7
        if score > best_score:
            best_score = score
            best = (rx, ry)
        elif score == best_score and best is not None:
            if (rx, ry) < best:
                best = (rx, ry)

    tx, ty = best
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        capture_bonus = 10**6 if (nx, ny) == (tx, ty) else 0
        # Also slightly prefer moves that reduce our distance more than the opponent's advantage indicates
        candidates.append((-(ds + 0.01 * (abs(nx - tx) + abs(ny - ty))) + (do - ds) * 0.001 + capture_bonus,
                           dx, dy))
    candidates.sort()
    return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]
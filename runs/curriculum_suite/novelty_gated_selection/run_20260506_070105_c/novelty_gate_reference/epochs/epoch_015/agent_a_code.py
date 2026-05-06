def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not res:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
        for dx2, dy2 in deltas:
            if inb(sx + dx2, sy + dy2):
                return [dx2, dy2]
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = w // 2, h // 2
    my_center = md(sx, sy, cx, cy)

    best = None
    bestv = -10**9
    for rx, ry in res:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        center_d = md(rx, ry, cx, cy)
        # Prefer stealing chances (opd > myd), then proximity, lightly prefer resources closer to center.
        v = (opd - myd) - 0.35 * myd + 0.05 * (my_center - center_d)
        if v > bestv:
            bestv = v
            best = (rx, ry)

    rx, ry = best
    # Choose best immediate move toward target; if blocked, try alternates.
    best_move = [0, 0]
    best_score = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = md(nx, ny, rx, ry)
        opd_now = md(ox, oy, rx, ry)
        # Maintain "denier" pressure: don't let opponent get much closer than us to the chosen resource.
        v = (opd_now - myd2) - 0.25 * myd2
        # Small penalty if moving away from the target direction.
        if dx != 0 or dy != 0:
            txstep = 0 if rx == sx else (1 if rx > sx else -1)
            tystep = 0 if ry == sy else (1 if ry > sy else -1)
            if dx != txstep and dy != tystep:
                v -= 0.05
        if v > best_score:
            best_score = v
            best_move = [dx, dy]

    return best_move if inb(sx + best_move[0], sy + best_move[1]) else [0, 0]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    role = (observation.get("self_role") or "").lower()
    evade = ("evader" in role) or ("runner" in role) or ("evasion" in role) or ("evasive" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not evade:
        step_x = 1 if ox > sx else (-1 if ox < sx else 0)
        step_y = 1 if oy > sy else (-1 if oy < sy else 0)
        # Cut-off point: move toward the opponent's next-step cell when possible.
        cx, cy = ox + step_x, oy + step_y
        if not valid(cx, cy):
            cx, cy = ox, oy
        best = None
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d1 = dist(nx, ny, ox, oy)
            d2 = dist(nx, ny, cx, cy)
            # Prefer closing to opponent, then to cut-off.
            v = (d1, d2, abs(nx - ox) + abs(ny - oy))
            if best is None or v < bestv:
                best = (dx, dy)
                bestv = v
        if best is None:
            return [0, 0]
        return [int(best[0]), int(best[1])]

    # Evader: maximize safety margin; bias away from direct pursuit.
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = dist(nx, ny, ox, oy)
        # Encourage moving off the pursuit line (perpendicular component).
        vx, vy = ox - sx, oy - sy
        wx, wy = nx - sx, ny - sy
        # Perpendicular magnitude squared ~ (vx*wy - vy*wx)^2
        perp = (vx * wy - vy * wx)
        v = (-d_op, -perp, abs(nx - 0) + abs(ny - 0))
        if best is None or v < bestv:
            best = (dx, dy)
            bestv = v
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
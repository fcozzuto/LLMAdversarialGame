def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if sx == ox and sy == oy:
        return [0, 0]

    best = (10**9, 10**9)
    best_move = (0, 0)

    # Two-step deterministic lookahead: minimize opponent distance with mild center preference.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy:
            return [dx, dy]
        d1 = dist(nx, ny, ox, oy)

        # Choose our best second step assuming opponent just stays (capture radius 0); helps evade zigzags.
        best_d2 = 10**9
        for ddx, ddy in moves:
            ex, ey = nx + ddx, ny + ddy
            if not ok(ex, ey):
                continue
            best_d2 = min(best_d2, dist(ex, ey, ox, oy))
        center_pen = abs(nx - cx) + abs(ny - cy)

        score = (d1 * 10 + best_d2, center_pen)
        # Tie-break: prefer diagonal over axial when same score to keep pressure.
        if score < best:
            best = score
            best_move = (dx, dy)
        elif score == best:
            if dx != 0 and dy != 0 and (best_move[0] == 0 or best_move[1] == 0):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
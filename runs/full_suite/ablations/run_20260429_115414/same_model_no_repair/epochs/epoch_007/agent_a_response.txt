def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            v = cheb(nx, ny, cx, cy)
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    # Evaluate each move by the best "advantage" resource it would pursue.
    best_move = None
    for dx, dy, nx, ny in moves:
        my_best = None
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # Strongly prefer resources where we are closer than opponent.
            val = (dop - dme) * 50 - dme
            if my_best is None or val > my_best:
                my_best = val
        # Small tie-breaker: prefer moves that also reduce distance to the most promising resource.
        if best_move is None or my_best > best_move[0]:
            best_move = (my_best, dx, dy)
        elif my_best == best_move[0]:
            # deterministic tie-break: lower chebyshev to opponent to reduce interference
            tb = cheb(nx, ny, ox, oy)
            cur_tb = cheb(sx + best_move[1], sy + best_move[2], ox, oy)
            if tb < cur_tb:
                best_move = (my_best, dx, dy)

    return [best_move[1], best_move[2]]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if legal(nx, ny):
                c += 1
        return c

    def corner_bias(x, y):
        # prefer positions that can trap opponent in corners when chasing
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # measure "distance to nearest corner" of opponent relative to our move
        mind = min(abs(ox - cx) + abs(oy - cy) for cx, cy in corners)
        myd = min(abs(x - cx) + abs(y - cy) for cx, cy in corners)
        # smaller myd helps control corners indirectly; mild weight
        return 0.05 * (myd - mind)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # capture ends game at radius 0; heuristic uses Chebyshev distance for diagonal movement
        dist = max(abs(nx - ox), abs(ny - oy))

        # wall pressure: avoid edges unless it helps (still chasing)
        dwall = min(nx, ny, w - 1 - nx, h - 1 - ny)
        wall_pen = 0.08 * (0 if dwall >= 2 else (2 - dwall))

        # obstacle dead-end penalty: fewer free neighbors is riskier
        fn = free_neighbors(nx, ny)
        dead_pen = 0.12 * (8 - fn if fn < 8 else 0)

        # "approach momentum": prefer reducing distance from previous to opponent
        cur_dist = max(abs(sx - ox), abs(sy - oy))
        approach = cur_dist - dist  # positive if closer

        # if opponent is in a corner, steer to its adjacent squares by favoring smaller dist and tighter trap
        trap = 0.0
        if (ox in (0, w - 1)) and (oy in (0, h - 1)):
            trap = -0.03 * (abs(nx - ox) + abs(ny - oy))

        score = dist - 0.6 * approach + wall_pen + dead_pen + corner_bias(nx, ny) + trap

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
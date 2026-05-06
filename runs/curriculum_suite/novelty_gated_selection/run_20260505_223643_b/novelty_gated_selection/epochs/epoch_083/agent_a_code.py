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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def approx_dist(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        m = dx if dx > dy else dy
        n = dy if dx > dy else dx
        return m  # Chebyshev for king-like movement

    opp_is_ahead_dir_penalty = 0
    for rx, ry in resources:
        pass

    best = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # choose a resource with best relative winning odds from next position
        move_score = None
        for rx, ry in resources:
            self_d = approx_dist((nx, ny), (rx, ry))
            opp_d = approx_dist((ox, oy), (rx, ry))
            # relative advantage: smaller self_d and larger opp_d is good
            # also bias toward reducing own distance to opponent to "intercept" sweep
            rel = (opp_d - self_d)
            block_bias = -abs(nx - ox) * 0.03 - abs(ny - oy) * 0.03
            row_col_sweep_bias = 0.0
            if ry == ny or rx == nx:
                row_col_sweep_bias = 0.12  # encourage aligning with a sweep line
            s = rel * 10.0 - self_d - opp_is_ahead_dir_penalty + block_bias + row_col_sweep_bias
            if move_score is None or s > move_score:
                move_score = s
        if move_score is None:
            continue
        if best is None or move_score > best:
            best = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target selection: maximize advantage to reach resource first (my_dist smaller than opponent_dist).
    if resources:
        best = None
        for tx, ty in resources:
            myd = cheb(sx, sy, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            advantage = opd - myd  # higher means more likely to be first
            # Tie-break toward closer and slightly toward center to stabilize.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_bias = abs(tx - cx) + abs(ty - cy)
            key = (-advantage, myd, center_bias, tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        tx, ty = best[1]

        # Move choice: among valid deltas, minimize remaining distance to target while preserving advantage.
        best_move = (0, 0)
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            myd2 = cheb(nx, ny, tx, ty)
            opd2 = cheb(ox, oy, tx, ty)  # opponent unchanged this turn
            advantage2 = opd2 - myd2
            # Prefer higher advantage, then lower remaining dist, then deterministic ordering.
            score = (-advantage2, myd2, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move to maximize distance from opponent and drift toward center.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)
        center = abs(nx - cx) + abs(ny - cy)
        score = (-d_op, center, dx, dy)  # maximize d_op => minimize -d_op
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
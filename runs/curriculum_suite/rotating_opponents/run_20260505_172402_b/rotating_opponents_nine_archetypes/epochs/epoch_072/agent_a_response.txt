def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def feasible(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        for tx, ty in [(dx, dy), (0, 0), (1 if sx < w - 1 else 0, 0), (0, 1 if sy < h - 1 else 0), (-1 if sx > 0 else 0, 0), (0, -1 if sy > 0 else 0)]:
            nx, ny = sx + tx, sy + ty
            if feasible(nx, ny):
                return [tx, ty]
        return [0, 0]

    # Choose a resource with maximal advantage; if we are already best, pursue the nearest one.
    best_res = resources[0]
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        key = (d_op - d_me, -d_me)  # prioritize where we are closer than opponent
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    # Evaluate one-step moves: minimize distance to target, and also discourage giving opponent better access.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not feasible(nx, ny):
            continue
        my_d = cheb(nx, ny, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        # If we can reduce our distance more than it helps opponent (op_d unchanged), strongly prioritize.
        # Also slightly prefer moves that keep us away from opponent unless it conflicts.
        sep = cheb(nx, ny, ox, oy)
        score = (-my_d, sep, -(op_d - my_d))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
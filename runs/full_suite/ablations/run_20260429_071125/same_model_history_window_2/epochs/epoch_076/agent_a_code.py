def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]
    if any(x == sx and y == sy for x, y in resources):
        return [0, 0]

    # Pick target that we are relatively closest to (or best to contest/intercept).
    best_target = None
    best_val = None
    for x, y in resources:
        d_us = cheb(sx, sy, x, y)
        d_op = cheb(ox, oy, x, y)
        val = (d_op - d_us) * 1000 - d_us  # prioritize being ahead; deterministic tie by coords
        if best_val is None or val > best_val or (val == best_val and (x, y) < best_target):
            best_val = val
            best_target = (x, y)

    tx, ty = best_target

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # If opponent is very close to the target, aim for interception point.
    d_op_to_t = cheb(ox, oy, tx, ty)
    intercept = None
    if d_op_to_t <= 2:
        ix = (tx + ox) // 2
        iy = (ty + oy) // 2
        ix = 0 if ix < 0 else (w - 1 if ix >= w else ix)
        iy = 0 if iy < 0 else (h - 1 if iy >= h else iy)
        if (ix, iy) not in obstacles:
            intercept = (ix, iy)

    target = intercept if intercept is not None else (tx, ty)

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d1 = cheb(nx, ny, target[0], target[1])
        # Secondary term: reduce opponent's progress toward original target.
        d2 = cheb(ox, oy, tx, ty)
        score = -d1 * 1000 + d2 - cheb(nx, ny, tx, ty)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
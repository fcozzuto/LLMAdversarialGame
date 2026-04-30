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
        return dx if dx >= dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Target selection: prefer resources where we are closer than opponent; otherwise choose nearest-to-me.
    best_t = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # score: higher is better
        score = (do - ds) * 100 - ds
        # deterministic tie-breaker
        tb = (rx, ry)
        key = (score, -tb[0], -tb[1])
        if best_score is None or key > best_score:
            best_score = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t

    # Move choice: greedy one-step that improves distance to target while making opponent farther.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dnt = cheb(nx, ny, tx, ty)
        dno = cheb(nx, ny, ox, oy)
        # also consider if opponent is closer to target than us after the move
        opp_to_t = cheb(ox, oy, tx, ty)
        my_to_t = dnt
        block = (opp_to_t - my_to_t)  # positive => we are closer
        key = (block, -dnt, dno, -dx, -dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
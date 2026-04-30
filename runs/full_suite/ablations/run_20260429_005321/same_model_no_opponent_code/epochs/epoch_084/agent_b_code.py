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

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Target the most "winnable" resource: maximize (op_dist - my_dist), tie-break by larger (and closer) distance spread.
    best_t = None
    best_s = -10**18
    best_d = 10**9
    for tx, ty in resources:
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        s = (od - md) * 100 - md  # strong preference for resources opponent is less able to reach
        # If both are close, slightly prefer nearer overall to commit.
        if s > best_s or (s == best_s and md < best_d):
            best_s = s
            best_d = md
            best_t = (tx, ty)

    tx, ty = best_t

    # Choose a move that reduces distance to target; discourage stepping into squares that let opponent close even more on same target.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        # Prefer lowering my distance; penalize moves that do not improve and that keep opponent advantage.
        improve = cheb(sx, sy, tx, ty) - my_d
        s = improve * 1000 - my_d * 3 + (op_d - my_d) * 2
        # Extra determinism: slight bias toward moving in the dominant direction to target (or staying if equal).
        s += (abs(nx - tx) < abs(sx - tx)) * 1 - (abs(nx - tx) > abs(sx - tx)) * 1
        if s > best_score or (s == best_score and (dx, dy) < best_move):
            best_score = s
            best_move = (dx, dy)

    # If somehow no valid move found (shouldn't happen), stay.
    if not valid(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
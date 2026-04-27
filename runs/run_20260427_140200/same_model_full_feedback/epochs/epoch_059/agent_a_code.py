def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Target selection: prefer resources we reach earlier than opponent.
    if resources:
        best = resources[0]
        best_score = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Big weight to race advantage; then favor closer.
            score = (d_op - d_me) * 1000 - d_me
            if best_score is None or score > best_score or (score == best_score and (rx, ry) < best):
                best_score = score
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    # Move selection: among valid moves, pick one that most reduces our distance to target.
    best_move = (0, 0)
    best_tuple = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Primary: minimize our distance to target.
        # Secondary: if tie, reduce opponent distance to our move (contest), else reduce opponent distance to target.
        opp_to_target = d_op
        opp_contest = cheb(nx, ny, ox, oy)
        tie = (nx, ny, dx, dy)
        tup = (d_me, opp_to_target, opp_contest, tie)
        if best_tuple is None or tup < best_tuple:
            best_tuple = tup
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # drift toward opponent's corner
        tx = w - 1 if ox < w - 1 else 0
        ty = h - 1 if oy < h - 1 else 0
        best = [0, 0]
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
                    best = [dx, dy]
        return best

    best_move = [0, 0]
    best_score = -10**18
    # Deterministically consider targets that matter most: those where we can get relatively closer.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        s_here = cheb(nx, ny, ox, oy)  # not direct, just breaks ties slightly
        score = -s_here * 0.01
        # evaluate best resource for this move
        move_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # prefer resources where we're closer (od - sd), but keep self distance low
            val = (od - sd) * 10 - sd
            if val > move_best:
                move_best = val
        score += move_best
        # tie-breaker: prefer smaller self distance to the globally best target for this move
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: lexicographic on (dx,dy) by preferring earlier dirs
            pass
    return [int(best_move[0]), int(best_move[1])]
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

    try:
        rem = int(observation.get("remaining_resource_count", 0) or 0)
    except:
        rem = 0
    late = rem <= 3

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        best_move = (0, 0)
        best_d = cheb(sx, sy, ox, oy)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best_d:
                best_d = d
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best = None
    best_score = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if late:
            # Late game: prioritize resources that are closer to us than them, and more "blocking".
            score = (opd - myd) * 10 - myd
        else:
            # Early/mid: greedily secure best race advantage, with mild attraction to low my distance.
            score = (opd - myd) * 8 + (10 - myd)
        # Deterministic tie-break: prefer smaller (rx,ry) in score ties.
        key = (score, -rx, -ry)
        if best is None or key > best_score:
            best_score = key
            best = (rx, ry)

    tx, ty = best
    cur_best = (0, 0)
    cur_d = 10**9

    # Move to the best neighbor (greedy distance to target), avoiding obstacles.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Tie-break: also prefer reducing opponent's ability to get there quickly.
        score2 = d - 0.25 * cheb(nx, ny, ox, oy)
        cur_score2 = cur_d - 0.25 * cheb(sx + cur_best[0], sy + cur_best[1], ox, oy)
        if d < cur_d or (d == cur_d and score2 < cur_score2) or (d == cur_d and score2 == cur_score2 and (dx, dy) < cur_best):
            cur_d = d
            cur_best = (dx, dy)

    # If stuck in invalid neighbors, stay.
    if not valid(sx + cur_best[0], sy + cur_best[1]):
        cur_best = (0, 0)
    return [int(cur_best[0]), int(cur_best[1])]
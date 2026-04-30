def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx = 0 if sx > w // 2 else w - 1
        ty = 0 if sy > h // 2 else h - 1
        best = (0, 0)
        bestv = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = cheb(nx, ny, tx, ty)
            if v < bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose a resource where we are relatively closer than the opponent; also prefer nearer absolute distance.
    best_t = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Steal priority if we are closer; otherwise still pick where opponent is far and we are not too slow.
        score = (d_op - d_me) * 100 - d_me
        # Encourage breaking ties by targeting the side nearer to our current quadrant.
        quad_bias = -((rx < w // 2) != (sx < w // 2)) * 3 - ((ry < h // 2) != (sy < h // 2)) * 3
        score += quad_bias
        if score > best_score:
            best_score, best_t = score, (rx, ry)

    tx, ty = best_t
    # Greedily step to reduce distance to target, but if blocked, try next-best options.
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            d_me = cheb(nx, ny, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # If we can arrive sooner than opponent by stepping, prioritize it.
            arrive_gap = (d_op - d_me)
            cand.append((-(arrive_gap * 1000) + d_me, dx, dy))
    cand.sort()
    if cand:
        return [int(cand[0][1]), int(cand[0][2])]
    return [0, 0]
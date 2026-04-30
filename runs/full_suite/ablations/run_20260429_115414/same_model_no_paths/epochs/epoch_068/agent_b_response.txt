def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in (observation.get("obstacles") or []):
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a resource where we are relatively closer than the opponent.
    best = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach at least as fast; use deterministic tie-breaks.
        key = (sd - od, sd, -tx, -ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    target = best[1] if best else (w // 2, h // 2)

    def obs_adj_pen(x, y):
        p = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic iteration order already in list; evaluate with integer scoring.
    best_move = (0, 0)
    best_score = None
    tx, ty = target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        opp_dist = cheb(nx, ny, ox, oy)
        toward = -sd * 10
        contest = (od - sd) * 6  # higher is better: we get closer than opponent
        sep = opp_dist * 2       # keep distance unless it conflicts with reaching target
        penalty = obs_adj_pen(nx, ny) * 5
        # Small bias toward the middle to reduce dead-ends.
        mid_bias = -(abs(nx - w // 2) + abs(ny - h // 2))
        score = toward + contest + sep + mid_bias - penalty
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
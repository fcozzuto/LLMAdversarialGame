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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Candidate targets: nearest-to-self and nearest-to-midpoint on the way to opponent
    midx, midy = (sx + ox) // 2, (sy + oy) // 2
    candidates = []
    if resources:
        best1 = None
        bestd1 = 10**9
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if d < bestd1 or (d == bestd1 and (best1 is None or (x, y) < best1)):
                bestd1, best1 = d, (x, y)
        candidates.append(best1)

        best2 = None
        bestd2 = 10**9
        for x, y in resources:
            d = cheb(midx, midy, x, y)
            if d < bestd2 or (d == bestd2 and (best2 is None or (x, y) < best2)):
                bestd2, best2 = d, (x, y)
        if best2 != best1:
            candidates.append(best2)
    else:
        candidates = [(w // 2, h // 2), (midx, midy)]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Score each move by: how much it improves self-to-target, how much it worsens opponent-to-target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        v = 0
        for tx, ty in candidates:
            ds_now = cheb(sx, sy, tx, ty)
            ds_next = cheb(nx, ny, tx, ty)
            do_now = cheb(ox, oy, tx, ty)
            do_next = cheb(ox, oy, tx, ty)  # opponent fixed this turn; implicit blocking via choosing shared target
            v += (ds_now - ds_next) * 100
            # Contest bonus: prefer targets where we are closer than opponent, without being too greedy
            gap = do_now - ds_now  # positive means we're closer
            v += gap * 3
            v -= abs(cheb(nx, ny, tx, ty) - do_now)  # keep tradeoff stable
        # Tie-break deterministically: prioritize lower (nx,ny)
        if v > best_val or (v == best_val and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
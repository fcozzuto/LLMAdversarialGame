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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If no resources, retreat/hold center-ish toward opponent to avoid being blocked too hard.
    if not resources:
        tx, ty = (w // 2), (h // 2)
        best = (None, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dist = cheb(nx, ny, tx, ty)
            score = -dist
            if score > best[1]:
                best = ((dx, dy), score)
        return [best[0][0], best[0][1]]

    # Choose a move that maximizes how much closer we become to some resource than the opponent is.
    best_move = (0, 0)
    best_score = -10**18

    # Precompute opponent distances
    opp_d = []
    for rx, ry in resources:
        opp_d.append(cheb(ox, oy, rx, ry))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate best "steal gap" over all resources
        best_gap = -10**18
        best_finish = -10**18
        for i, (rx, ry) in enumerate(resources):
            our_dist = cheb(nx, ny, rx, ry)
            gap = opp_d[i] - our_dist  # positive means we are closer than opponent
            if gap > best_gap:
                best_gap = gap
            # Encourage moves that can grab quickly (small dist)
            finish = 10 - our_dist
            if finish > best_finish:
                best_finish = finish

        # Additional bias: avoid moving farther from the currently best resource we target via gap
        # Tie-breaker uses lexicographic order due to fixed iteration ordering.
        score = best_gap * 100 + best_finish
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
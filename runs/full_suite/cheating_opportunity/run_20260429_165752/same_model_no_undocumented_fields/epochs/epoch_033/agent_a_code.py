def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        bestd = None
        bestm = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd = d
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    best_score = None
    best_move = (0, 0)
    # Score: capture advantage = (opp_dist - my_dist), prefer smaller my_dist to secure.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_best = None
        opp_for_my_best = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d
            # For a given move, pick the most favorable target deterministically.
            cand = (adv, -my_d, -rx, -ry)  # maximize adv and -my_d, deterministic tie
            if my_best is None or cand > my_best:
                my_best = cand
                opp_for_my_best = opp_d
        # Convert to single move score
        adv, neg_my_d, _, _ = my_best
        my_d = -neg_my_d
        move_score = (adv, -my_d, -abs(nx - ox) - abs(ny - oy), -nx, -ny)
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
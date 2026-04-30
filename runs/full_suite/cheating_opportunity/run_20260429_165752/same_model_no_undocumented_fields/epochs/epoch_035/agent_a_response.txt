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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in moves if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    # Choose move by evaluating best "claimable" resource after the move.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Heuristic over resources: prefer resources where we are closer (or at least not worse),
        # and prioritize reducing our distance while increasing opponent's.
        local_best = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # If we can "claim" (we're closer), reward strongly; otherwise, still consider far-away resources.
            claim = d_op - d_me  # positive means we are closer
            # Extra: if moving near opponent, discourage when contesting.
            near_op = 1 if cheb(nx, ny, ox, oy) <= 1 else 0
            score = 0
            if claim > 0:
                score += 1000 * claim
            else:
                score -= 60 * (-claim)  # contested or worse
                score += 20 * (8 - min(d_op, 8))  # resources opponent is unlikely to reach fast
            score += (20 - d_me) * 3
            score -= near_op * (12 if claim <= 0 else 2)
            # Slight bias toward resources not "too close" to opponent already
            score -= (max(0, 4 - d_op)) * (3 if claim <= 0 else 1)
            if score > local_best:
                local_best = score
        if resources:
            # If no resources, local_best remains huge negative; but resources exists if not empty.
            total = local_best
        else:
            # No resources visible: drift to the opposite corner from opponent (deterministic).
            tx, ty = (0 if ox > (w - 1) // 2 else w - 1), (0 if oy > (h - 1) // 2 else h - 1)
            total = -(cheb(nx, ny, tx, ty))
        # Tie-break deterministically: prefer moves that keep distance from opponent decreasing claim chances.
        total -= 0.01 * cheb(nx, ny, ox, oy)
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
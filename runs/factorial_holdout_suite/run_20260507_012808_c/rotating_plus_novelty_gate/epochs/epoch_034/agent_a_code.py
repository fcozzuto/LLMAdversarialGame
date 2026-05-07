def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    turns_remaining = observation.get("turns_remaining", 1)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not valid(sx, sy):
        sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
        sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
        if not valid(sx, sy):
            return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd, best = d, [dx, dy]
        return best

    # Choose a resource: prioritize winning it (self_dist <= opp_dist), then smallest self_dist,
    # then a mild preference for resources that remain finishable given turns_remaining.
    best_key = None
    best_res = resources[0]
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        finish_bonus = 0
        if ds <= turns_remaining:
            finish_bonus = 0  # no penalty
        else:
            finish_bonus = 1  # discourage unlikely finishes
        # key: win first, then self speed, then opponent slowness, then finishability
        win = 0 if ds <= do else 1
        key = (win, ds + finish_bonus, -do)
        if best_key is None or key < best_key:
            best_key, best_res = key, [rx, ry]

    rx, ry = best_res
    # Step towards target with obstacle-aware local minimization; also apply small "block" bias if close.
    close_to_opp = (cheb(sx, sy, ox, oy) <= 2)
    best = [0, 0]
    best_score = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dself = cheb(nx, ny, rx, ry)
        dopp_to_target = cheb(ox, oy, rx, ry)
        # If we're not winning, prioritize reducing our lead; if winning, keep pressuring quickly.
        score = dself
        if dself > do:  # do from current step approx
            score = dself + 2 * cheb(nx, ny, ox, oy)
        if close_to_opp and score <= best_score:
            score += 0 if cheb(nx, ny, ox, oy) > 0 else 3
        if score < best_score:
            best_score, best = score, [dx, dy]
    return best
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    # Strategy change: contest-aware target selection (prefer resources that are closer for us than for opponent,
    # and also steer away from opponent when our lead is small).
    opp_dist_now = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = -10**18

    center = ((w - 1) // 2, (h - 1) // 2)

    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        if not resources:
            cx, cy = center
            score = -cheb(nx, ny, cx, cy) - (2 if cheb(nx, ny, ox, oy) < opp_dist_now else 0)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
            continue

        # Choose best resource under (lead, safety) criterion
        best_res_score = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer than opponent
            # Favor taking leads; also slightly prefer farther resources only when lead is similar,
            # and avoid moving into opponent's immediate neighborhood.
            safety = cheb(nx, ny, ox, oy)
            rscore = (lead * 1000) - ds * 3 + (safety * 2) - (do * 0.5)
            # If opponent can reach at same time or sooner, penalize more.
            if lead <= 0:
                rscore -= 200 + (0 if lead == 0 else (-lead) * 5)
            if rscore > best_res_score:
                best_res_score = rscore

        # Tie-breaker: prefer not to get adjacent to opponent unless we have a strong lead move
        adj_pen = 0
        if cheb(nx, ny, ox, oy) <= 1:
            adj_pen = 150
        score = best_res_score - adj_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
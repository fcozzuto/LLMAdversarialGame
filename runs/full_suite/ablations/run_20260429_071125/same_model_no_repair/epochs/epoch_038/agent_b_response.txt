def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    adj_obs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]

    # Threat: opponent can grab something immediately
    threat = 0
    if resources:
        for rx, ry in resources:
            if cheb(ox, oy, rx, ry) <= 1:
                threat = 1
                break

    bestmv = (0, 0)
    best = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # Obstacle avoidance
        obs_pen = 0
        for ddx, ddy in adj_obs:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) in occ:
                obs_pen -= 7

        # Resource scoring: prioritize resources where we're closer; otherwise deny best gaps.
        if resources:
            best_my_closer = -10**18
            best_adv = -10**18
            best_opp_closer = 10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                gap = opd - myd  # positive => we are closer
                if gap > best_my_closer:
                    best_my_closer = gap
                # Prefer progress toward our best target (small myd if we're ahead)
                if gap >= 0 and myd < best_opp_closer:
                    best_opp_closer = myd
                if opd - myd > best_adv:
                    best_adv = opd - myd
            # If we're generally behind, still move to reduce "opponent closeness advantage"
            score = best_my_closer * 280 + (-best_opp_closer) * 18 + best_adv * 30
        else:
            score = 0

        # If opponent has immediate threat, maximize distance from them
        if threat:
            score += cheb(nx, ny, ox, oy) * 120

        # Small tie-breaker toward center for determinism when equal
        cx, cy = (w - 1) // 2, (h - 1) // 2
        score += -cheb(nx, ny, cx, cy) * 1

        score += obs_pen

        if score > best:
            best = score
            bestmv = (dx, dy)

    return [bestmv[0], bestmv[1]]
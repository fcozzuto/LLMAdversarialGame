def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1, 0) if (sx + sy) % 2 == 0 else (w - 1, h - 1)
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            score = -d
            if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)
        return [best[1], best[2]]

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Race-aware: prefer resources where we close the gap vs opponent, and avoid giving them faster access.
        min_dist_self = 10**9
        min_dist_opp = 10**9
        best_local = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Primary: maximize (opponent_time - our_time). Secondary: prefer shorter our_time.
            gap = do - ds
            val = gap * 10 - ds
            # Small deterministic preference for center-ish to reduce tie cycling.
            val -= abs(rx - (w - 1) / 2) * 0.01 + abs(ry - (h - 1) / 2) * 0.01
            if val > best_local:
                best_local = val
            if ds < min_dist_self: min_dist_self = ds
            if do < min_dist_opp: min_dist_opp = do

        # Extra nudge: if opponent is closer to some resource, try to move to reduce our worst-case distance among top threats.
        # Deterministic approximation via worst among resources with do <= min_dist_opp + 1.
        threat_pen = 0
        for rx, ry in resources:
            do = cheb(ox, oy, rx, ry)
            if do <= min_dist_opp + 1:
                ds = cheb(nx, ny, rx, ry)
                if ds > do: threat_pen += (ds - do)
        score = best_local - threat_pen

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
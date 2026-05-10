def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def best_opp_dist(tx, ty):
        best = 10**9
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                d = cheb(nx, ny, tx, ty)
                if d < best:
                    best = d
        return best if best < 10**9 else cheb(ox, oy, tx, ty)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Pick a "target" resource that we would likely get; score by our distance and contest with opponent.
        min_score = 10**18
        chosen = res[0]
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            # favor closer; tie-break by farther from opponent (so we can secure it)
            o_d = best_opp_dist(rx, ry)
            s = d * 10 - o_d
            if s < min_score:
                min_score = s
                chosen = (rx, ry)

        rx, ry = chosen
        my_d = cheb(nx, ny, rx, ry)
        opp_d = best_opp_dist(rx, ry)

        # Bonus if we can arrive strictly sooner; otherwise penalize.
        contest = 0
        if my_d < opp_d:
            contest = 50 + (opp_d - my_d) * 5
        elif my_d == opp_d:
            contest = -8
        else:
            contest = -(my_d - opp_d) * 12

        # Small center bias to keep moving instead of oscillating.
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center_bias = -cheb(nx, ny, cx, cy)

        # Avoid "staying" if there exists an improving move.
        stay_pen = 4 if (dx == 0 and dy == 0) else 0

        val = -my_d * 10 + contest + center_bias - stay_pen
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
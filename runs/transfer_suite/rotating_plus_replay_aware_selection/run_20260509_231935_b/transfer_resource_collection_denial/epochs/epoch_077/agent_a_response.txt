def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        if (nx, ny) in obs:
            continue

        my_min = 10**9
        opp_min = 10**9
        my_cnt = 0
        opp_cnt = 0
        collected = 0
        for rx, ry in res:
            d_m = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            if (nx, ny) == (rx, ry):
                collected = 1
            if d_m < my_min:
                my_min = d_m
                my_cnt = 1
            elif d_m == my_min:
                my_cnt += 1
            if d_o < opp_min:
                opp_min = d_o
                opp_cnt = 1
            elif d_o == opp_min:
                opp_cnt += 1

        # Score: prioritize immediate collection, then win race on closest resource.
        # Tie-break deterministically using x then y.
        score = 0
        score += collected * 1000000
        score += (opp_min - my_min) * 2000
        # Encourage progressing toward multiple nearest resources evenly.
        score += -my_min * 5 - opp_min * 1
        score += -my_cnt * 2 + opp_cnt * 1
        score += (nx - sx) * 0.01 + (ny - sy) * 0.001

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]
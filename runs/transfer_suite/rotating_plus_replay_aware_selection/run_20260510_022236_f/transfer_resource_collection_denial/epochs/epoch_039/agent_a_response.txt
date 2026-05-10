def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    res = [(int(x), int(y)) for x, y in resources if 0 <= int(x) < w and 0 <= int(y) < h]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not res or (sx, sy) in obs:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    def safety(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                x, y = nx + dx, ny + dy
                if (x, y) in obs:
                    p -= 2
        return p

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue
        if resources and (nx, ny) in res:
            my_pick = cheb(nx, ny, nx, ny)
        my_dist_best = 10**9
        opp_dist_best = 10**9
        opp_threat = 0
        for rx, ry in res:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if od <= 1 and md <= 2:
                opp_threat += 2
            if md < my_dist_best:
                my_dist_best = md
                opp_dist_best = od
        # Prefer moves that let us reach a resource earlier than opponent, plus safety and slight center bias
        center_bias = -abs((nx - (w - 1) / 2.0)) - abs((ny - (h - 1) / 2.0))
        score = (opp_dist_best - my_dist_best) + 0.15 * (opp_dist_best) + 0.05 * center_bias + safety(nx, ny) - opp_threat
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
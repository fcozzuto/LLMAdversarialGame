def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opp_pos[0], opp_pos[1]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd or (d == bestd and (best is None or (dx, dy) < best)):
                    bestd = d
                    best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best_move = (0, 0)
    best_score = -10**18
    best_res_dist = 10**9

    res_list = [tuple(r) for r in resources]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        score = -10**18
        local_best_dist = 10**9
        for rx, ry in res_list:
            our = cheb(nx, ny, rx, ry)
            opp = cheb(ox, oy, rx, ry)
            # prioritize capturing resources closer than opponent; encourage immediate pickup
            s = (opp - our) * 10 - our
            if our == 0:
                s += 1000000
            if (s > score) or (s == score and our < local_best_dist):
                score = s
                local_best_dist = our

        # small deterministic tiebreakers
        if (score > best_score) or (score == best_score and local_best_dist < best_res_dist) or \
           (score == best_score and local_best_dist == best_res_dist and (dx, dy) < best_move):
            best_score = score
            best_res_dist = local_best_dist
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
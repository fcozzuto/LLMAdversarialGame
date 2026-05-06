def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(x, lo, hi):
        if x < lo: return lo
        if x > hi: return hi
        return x

    if not resources:
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
            if (nx, ny) in obstacles: 
                continue
            d = cheb(nx, ny, ox, oy)
            score = -d
            if score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Tie-break deterministically by preferring smaller dx,dy sequence order.
    best_score = 10**18
    best_dx = 0
    best_dy = 0
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue

        # Prefer approaching resources that opponent is unlikely to capture first.
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            if d_my < my_best:
                my_best = d_my
            d_op = cheb(ox, oy, rx, ry)
            if d_op < opp_best:
                opp_best = d_op

        # Heuristic:
        # - Minimize distance to nearest resource
        # - If close race, avoid allowing opponent to be strictly closer
        # - Also prefer increasing distance from opponent slightly to reduce contest success
        dist_penalty = my_best * 10
        contest = opp_best - my_best  # positive means we're closer to some resource
        # If opponent is closer (contest negative), penalize more.
        race_penalty = 0
        if contest < 0:
            race_penalty = (-contest) * 30
        # Encourage moving away from opponent mildly.
        opp_dist = cheb(nx, ny, ox, oy)
        opp_bonus = -opp_dist  # more distance => smaller score
        score = dist_penalty + race_penalty + opp_bonus

        if score < best_score or (score == best_score and (dx, dy) < (best_dx, best_dy)):
            best_score = score
            best_dx = dx
            best_dy = dy

    return [int(best_dx), int(best_dy)]
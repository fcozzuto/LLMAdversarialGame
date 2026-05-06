def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_dist(px, py):
        bd = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < bd:
                bd = d
        return bd

    def best_target_for(px, py):
        best = resources[0]
        bestd = cheb(px, py, best[0], best[1])
        for rx, ry in resources[1:]:
            d = cheb(px, py, rx, ry)
            if d < bestd:
                bestd = d
                best = (rx, ry)
        return best, bestd

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_my = nearest_dist(sx, sy)
    cur_opp = nearest_dist(ox, oy)
    opp_target, _ = best_target_for(ox, oy)

    best_score = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue

        my_d = nearest_dist(nx, ny)
        if my_d == 0:
            score = 10**8
        else:
            score = (cur_opp - my_d) * 1000 - my_d

        # Additional pressure: move toward the resource currently nearest to the opponent
        t_d = cheb(nx, ny, opp_target[0], opp_target[1])
        cur_t_d = cheb(sx, sy, opp_target[0], opp_target[1])
        score += (cur_t_d - t_d) * 50

        # Small deterministic tie-breaker: prefer not moving away from any resource generally
        if cur_my > 0:
            score += (cur_my - my_d) * 1

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move
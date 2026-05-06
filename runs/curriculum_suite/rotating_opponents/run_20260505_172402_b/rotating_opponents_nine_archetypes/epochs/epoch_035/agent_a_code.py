def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)
    opp_edge = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)

    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not free(nx, ny):
            continue

        if resources:
            best_res = 10**9
            nearest_edge_res = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < best_res:
                    best_res = d
                if rx == 0 or rx == w - 1 or ry == 0 or ry == h - 1:
                    if d < nearest_edge_res:
                        nearest_edge_res = d
            dist_term = -best_res
            edge_term = 0
            if nearest_edge_res < 10**9:
                edge_term = -0.8 * nearest_edge_res
        else:
            dist_term = 0
            edge_term = 0

        d_opp = cheb(nx, ny, ox, oy)
        # Prefer positions that are not too close to opponent (avoid contest unless we can reach resources)
        contest_penalty = 0
        if d_opp <= 1:
            contest_penalty = 2.5
        # Interceptor bias: if opponent is not on edge, try to reduce distance to opponent by moving diagonally-ish
        interc_bias = 0
        if not opp_edge:
            interc_bias = 0.25 * (d_opp * -1)

        score = dist_term + edge_term + (-0.9 * d_opp) - contest_penalty + interc_bias
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]
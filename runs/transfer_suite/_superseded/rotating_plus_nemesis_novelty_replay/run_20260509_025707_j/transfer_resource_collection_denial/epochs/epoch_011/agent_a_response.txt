def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    res_set = set((p[0], p[1]) for p in resources)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_dist(px, py, target_set):
        best = None
        for rx, ry in target_set:
            d = cheb(px, py, rx, ry)
            if best is None or d < best:
                best = d
        return best if best is not None else 10**9

    # One-step lookahead: maximize distance advantage toward the "most favorable" resource
    best_key = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        # if we can collect now, prioritize strongly
        collected = 1 if (nx, ny) in res_set else 0

        # proxy: our nearest resource advantage vs opponent nearest resource
        our_best = best_dist(nx, ny, res_set)
        opp_best = best_dist(ox, oy, res_set)

        # target-bias: prefer moving toward a resource that is far for opponent
        # (reduces chance opponent snatches "our" target)
        best_adv_to_res = -10**9
        for rx, ry in res_set:
            a = cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)
            if a > best_adv_to_res:
                best_adv_to_res = a

        # tie-breakers: closer to any resource; and deterministic ordering by move delta
        key = (collected, best_adv_to_res, opp_best - our_best, -our_best, -(rx + ry) if False else 0, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx if valid(sx + dx, sy + dy) else 0, dy if valid(sx + dx, sy + dy) else 0)

    return [int(best_move[0]), int(best_move[1])]
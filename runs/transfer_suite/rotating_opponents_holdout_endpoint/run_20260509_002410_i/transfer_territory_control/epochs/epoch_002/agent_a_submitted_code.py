def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles", []) or []
    obs = set(obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = observation.get("resources", []) or []
    res = resources[0] if resources else None
    if resources:
        best_r = None
        best_d = 10**18
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if d < best_d or (d == best_d and (rx, ry) < best_r):
                best_d = d
                best_r = (rx, ry)
        res = best_r

    scores = observation.get("scores", {}) or {}
    self_score = scores.get("self", scores.get("me", 0))
    opp_score = scores.get("opponent", scores.get("them", 0))
    behind = self_score <= opp_score

    def eval_move(nx, ny):
        d_to_opp = abs(ox - nx) + abs(oy - ny)
        if behind:
            if res is not None:
                d_to_res = abs(res[0] - nx) + abs(res[1] - ny)
                return -d_to_res + 0.01 * d_to_opp
            return 0.01 * d_to_opp
        return d_to_opp

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        val = eval_move(nx, ny)
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]
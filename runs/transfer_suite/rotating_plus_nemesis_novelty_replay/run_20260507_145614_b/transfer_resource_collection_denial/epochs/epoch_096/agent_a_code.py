def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # If no resources, drift to center-ish while staying safe.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        step_x = 0 if sx == tx else (1 if tx > sx else -1)
        step_y = 0 if sy == ty else (1 if ty > sy else -1)
        nx, ny = sx + step_x, sy + step_y
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return [step_x, step_y]
        # fallback safe move
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    # Bias toward contesting opponent's row/col line if aligned.
    intercept_x = None
    intercept_y = None
    if oy == sy:
        intercept_x = ox  # try to match x while moving on that row
    if ox == sx:
        intercept_y = oy  # try to match y while moving on that col
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        # Compute advantage over opponent to the closest reachable resource.
        self_best = 10**9
        opp_best = 10**9
        adv_best = -10**9
        nearest = None

        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < self_best:
                self_best = ds; nearest = (rx, ry)
            if do < opp_best:
                opp_best = do
            adv = do - ds
            if adv > adv_best:
                adv_best = adv

        # Value: prioritize resources where we have positive/large advantage.
        # Secondary: reduce our distance; tertiary: keep distance from opponent unless contesting.
        dist_to_nearest = self_best
        opp_dist_to_nearest = cheb(ox, oy, nearest[0], nearest[1]) if nearest else opp_best
        keep_away = cheb(nx, ny, ox, oy)

        val = 1000 * adv_best - 10 * dist_to_nearest + 0.3 * keep_away - 0.01 * opp_dist_to_nearest

        # Extra deterministic intercept pressure when aligned.
        if intercept_x is not None and ny == sy:
            val += 50 * (w - 1 - abs(nx - intercept_x))
        if intercept_y is not None and nx == sx:
            val += 50 * (h - 1 - abs(ny - intercept_y))

        # Tie-break deterministically: prefer smaller dx, then smaller dy.
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move
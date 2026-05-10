def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)
    turns_remaining = observation.get("turns_remaining", 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res_set = set(tuple(r) for r in resources)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (-10**18, None)
    late = 1 if turns_remaining <= 8 else 0  # shift toward greedy late

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        if not resources:
            return [0, 0]

        val = 0
        if (nx, ny) in res_set:
            val += 10**6

        my_best = 10**9
        opp_best = 10**9
        margin_best = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd < my_best: my_best = myd
            if opd < opp_best: opp_best = opd
            # prefer resources we can reach earlier than opponent
            m = (opd - myd)
            if m > margin_best: margin_best = m

        # win race margin; late game more weight on immediate closeness
        val += (margin_best * 10**4)
        val += (opp_best - my_best) * (200 if late else 80)
        val += -my_best * (50 if late else 20)

        if val > best[0]:
            best = (val, (dx, dy))

    return [best[1][0], best[1][1]]
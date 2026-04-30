def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cheb(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    cand = []
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = set(tuple(p) for p in resources)

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        valid = 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles
        if not valid:
            cand.append(((-10**9, dx, dy)))
            continue

        score = 0
        if (nx, ny) in res_set:
            score += 1000

        if (nx, ny) == (ox, oy):
            score -= 500

        my_pos = (nx, ny)
        best_gain = -10**9
        my_min = 10**9
        opp_min = 10**9
        for r in res_set:
            r = (r[0], r[1])
            myd = cheb(my_pos, r)
            opd = cheb((ox, oy), r)
            if myd < my_min:
                my_min = myd
            if opd < opp_min:
                opp_min = opd
            gain = opd - myd
            if gain > best_gain:
                best_gain = gain

        score += best_gain * 10 - my_min
        if opp_min == 0:
            score -= 200
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                    score -= 2
        cand.append(((-score, dx, dy)))

    best = min(cand)
    return [best[1], best[2]]
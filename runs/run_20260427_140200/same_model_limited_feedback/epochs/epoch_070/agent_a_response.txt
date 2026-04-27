def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = sx + ddx, sy + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [ddx, ddy]
        return [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best_r = None
    best_val = 10**9
    for r in resources:
        d1 = cheb((sx, sy), r)
        d2 = cheb((ox, oy), r)
        val = d1 - 0.5 * d2
        if val < best_val:
            best_val = val
            best_r = r
    tx, ty = best_r

    deltas = (-1, 0, 1)
    best_move = [0, 0]
    best_score = 10**9
    for ddx in deltas:
        for ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            ds = cheb((nx, ny), (tx, ty))
            # opponent "next" move heuristic: assume they move toward target if possible
            odx = 0 if ox == tx else (1 if tx > ox else -1)
            ody = 0 if oy == ty else (1 if ty > oy else -1)
            ax, ay = ox + odx, oy + ody
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                dop = cheb((ax, ay), (tx, ty))
            else:
                dop = cheb((ox, oy), (tx, ty))
            score = ds - 0.45 * dop + 0.05 * cheb((nx, ny), (ox, oy))
            if score < best_score:
                best_score = score
                best_move = [ddx, ddy]
    return [int(best_move[0]), int(best_move[1])]
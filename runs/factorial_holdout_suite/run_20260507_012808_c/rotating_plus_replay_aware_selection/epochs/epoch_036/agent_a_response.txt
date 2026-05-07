def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def king_dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    if not resources:
        tx, ty = 0, 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    opp_target = resources[0]
    best_opp_d = king_dist((ox, oy), opp_target)
    for r in resources[1:]:
        d = king_dist((ox, oy), r)
        if d < best_opp_d:
            best_opp_d, opp_target = d, r

    def score_move(nx, ny):
        s = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                s += 1000
                break
        my_d = king_dist((nx, ny), opp_target)
        s += 120 * (best_opp_d - my_d)  # intercept/deny pressure
        if resources:
            best_my_r = resources[0]
            best_my_d = king_dist((nx, ny), best_my_r)
            for r in resources[1:]:
                d = king_dist((nx, ny), r)
                if d < best_my_d:
                    best_my_d, best_my_r = d, r
            s += 35 * (0 - best_my_d)  # progress to any resource
        # slight obstacle avoidance: prefer moves with fewer adjacent obstacles
        pen = 0
        for ax, ay in dirs:
            ax2, ay2 = nx + ax, ny + ay
            if (ax2, ay2) in obstacles:
                pen += 1
        s -= 8 * pen
        return s

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score_move(nx, ny)
        if sc > best[0]:
            best = (sc, dx, dy)

    if best[0] == -10**18:
        return [0, 0]
    return [best[1], best[2]]
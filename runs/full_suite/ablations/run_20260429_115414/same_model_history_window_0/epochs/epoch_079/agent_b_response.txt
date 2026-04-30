def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = -10**18

    res_list = [tuple(p) for p in resources]
    if not res_list:
        return [0, 0]

    res_set = set(res_list)
    def nearest_dist2(px, py):
        bd = 10**18
        for rx, ry in res_list:
            d = dist2(px, py, rx, ry)
            if d < bd:
                bd = d
        return bd

    opp_d0 = nearest_dist2(ox, oy)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in res_set:
            score = 10**9
        else:
            sd = nearest_dist2(nx, ny)
            score = -sd
            score += 0.2 * (opp_d0 - sd)  # relative pressure
        # small tie-breaker toward reducing Manhattan to opponent (block/contest center)
        score += -0.01 * (abs(nx - ox) + abs(ny - oy))
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
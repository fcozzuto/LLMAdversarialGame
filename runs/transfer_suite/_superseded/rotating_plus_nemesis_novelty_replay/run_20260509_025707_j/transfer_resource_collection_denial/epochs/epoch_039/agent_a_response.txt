def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            rx, ry = r[0], r[1]
            if ok(rx, ry):
                res.append((rx, ry))
    if not res:
        return [0, 0]

    best = None  # (adv, -opp_goal, my_goal, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Choose the resource that maximizes my advantage over opponent.
        best_adv = None
        best_opp_d = None
        best_my_d = None
        for rx, ry in res:
            my_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            adv = opp_d - my_d
            if best_adv is None or adv > best_adv or (adv == best_adv and (opp_d < best_opp_d or (opp_d == best_opp_d and my_d < best_my_d))):
                best_adv = adv
                best_opp_d = opp_d
                best_my_d = my_d
        cand = (best_adv, -best_opp_d, best_my_d, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[3], best[4]]
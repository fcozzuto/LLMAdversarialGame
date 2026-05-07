def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def eval_cell(nx, ny):
        if nx == ox and ny == oy:
            return -10**9
        if not res:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            return -(abs(nx - cx) + abs(ny - cy)) + 0.1 * (md((nx, ny), (ox, oy)))

        best = -10**18
        for rx, ry in res:
            my_d = md((nx, ny), (rx, ry))
            op_d = md((ox, oy), (rx, ry))
            if my_d == 0:
                cand = 2000 - op_d
            else:
                lead = op_d - my_d
                if lead >= 0:
                    cand = lead * 10 - my_d * 2
                else:
                    cand = lead * 14 - my_d * 3  # being behind: try to still steal/deny
            best = max(best, cand)

        nearest = min((md((nx, ny), (rx, ry)) for rx, ry in res), default=0)
        enemy_pressure = md((nx, ny), (ox, oy))
        return best - nearest * 0.5 + enemy_pressure * 0.05

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = eval_cell(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]
    return best_move
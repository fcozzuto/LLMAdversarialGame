def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (w - 1, h - 1)) or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for o in obs_list:
        if o is None:
            continue
        try:
            obstacles.add((int(o[0]), int(o[1])))
        except Exception:
            pass

    res_list = observation.get("resources", []) or []
    resources = []
    for r in res_list:
        try:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def best_resource_score(nx, ny):
        if not resources:
            return 0
        best = -10**18
        for rx, ry in resources:
            myd = dist((nx, ny), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            if myd == 0:
                return 10**12
            val = (opd - myd) * 100 - myd
            if val > best:
                best = val
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = best_resource_score(nx, ny)
        if (nx, ny) == (ox, oy):
            v -= 10**6
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]
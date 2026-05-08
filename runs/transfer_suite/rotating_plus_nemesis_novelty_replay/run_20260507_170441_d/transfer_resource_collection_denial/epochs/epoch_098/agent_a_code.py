def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources") or []
    if isinstance(resources, dict):
        resources = list(resources.keys())

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(a, b):
        x1, y1 = a
        x2, y2 = b
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best = (-10**18, 10**18)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            s = (nx, ny)
            o = (ox, oy)
            adv_best = -10**18
            ds_best = 10**18
            for r in resources:
                if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                    continue
                rr = (r[0], r[1])
                ds = dist8(s, rr)
                do = dist8(o, rr)
                adv = do - ds
                if adv > adv_best or (adv == adv_best and ds < ds_best):
                    adv_best = adv
                    ds_best = ds
            cand = (adv_best, ds_best)
        else:
            # No resources: drift toward center, keep deterministic.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            dcent = abs(nx - cx) + abs(ny - cy)
            cand = (-dcent, dcent)
        if cand[0] > best[0] or (cand[0] == best[0] and cand[1] < best[1]):
            best = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    # If already on a resource, don't waste a turn.
    if (sx, sy) in set(res):
        return [0, 0]

    opp_targets = res
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        my_best = 10**9
        # Choose target resource where my advantage is maximized (opp slower than me).
        # Minimize (my_dist - opp_dist) primarily, then tie-break by my_dist (closer).
        local_best = (10**9, 10**9)
        for rx, ry in opp_targets:
            my_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            adv = my_d - opp_d
            cand = (adv, my_d)
            if cand < local_best:
                local_best = cand
        # Secondary tie-break: also prefer moves that reduce distance to the globally nearest resource from current pos.
        if local_best[0] < my_best or (local_best[0] == my_best and nx == nx):  # deterministic structure
            # compute nearest-from-current tie-break
            nearest_now = 10**9
            for rx, ry in res:
                dnow = md(nx, ny, rx, ry)
                if dnow < nearest_now:
                    nearest_now = dnow
            key = (local_best[0], local_best[1], nearest_now, dx, dy)
            if best_move is None or key < best_move[0]:
                best_move = (key, dx, dy)

    return [best_move[1], best_move[2]] if best_move else [0, 0]
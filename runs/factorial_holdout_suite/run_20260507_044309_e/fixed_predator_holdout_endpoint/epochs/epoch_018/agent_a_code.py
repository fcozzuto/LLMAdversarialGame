def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    res = [tuple(r) for r in resources]
    res_set = set(res)

    if (sx, sy) in res_set:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Race heuristic: maximize (opp_dist - self_dist) for the best contested resource.
        best_local = -10**18
        best_self_d = 10**9
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Positive means we are closer (good); negative means opponent closer (deny by moving toward it).
            v = (do - ds) * 10 - ds
            if v > best_local or (v == best_local and ds < best_self_d):
                best_local = v
                best_self_d = ds

        # Tie-break: prefer moving that reduces distance to some resource while staying in-bounds.
        if best_local > best_val:
            best_val = best_local
            best = [dx, dy]
        elif best_local == best_val and best is not None:
            cur_sd = man(sx, sy, res_set and (sx, sy) and (sx, sy)[0] or sx, sy)
            if best_self_d < cur_sd:
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
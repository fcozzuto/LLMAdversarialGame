def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    endgame = int(observation.get("remaining_resource_count", 999) or 999) <= 5

    obs_set = set()
    for ob in obstacles:
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            obs_set.add((int(ob[0]), int(ob[1])))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        sd_m = man(sx, sy, tx, ty)
        od_m = man(ox, oy, tx, ty)
        sd_c = cheb(sx, sy, tx, ty)
        od_c = cheb(ox, oy, tx, ty)
        if endgame:
            key = (sd_m, sd_c, -od_m)
        else:
            secure = 1 if sd_m <= od_m else 0
            lead = od_m - sd_m
            key = (0 if secure else 1, -lead, sd_m, sd_c)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        my_dist = man(nx, ny, tx, ty)
        opp_dist = man(ox, oy, tx, ty)
        step_toward = my_dist
        opp_pressure = opp_dist - my_dist  # higher means we get closer relative to opponent
        block_bonus = 0
        if (nx, ny) == (ox, oy):
            block_bonus = 5
        key = (step_toward, -opp_pressure, -block_bonus, abs((tx - nx)) + abs((ty - ny)))
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
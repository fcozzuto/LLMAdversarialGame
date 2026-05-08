def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_obstacle_penalty(x, y):
        # mild deterministic avoidance of stepping near obstacles
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    pen += 2
        return pen

    # Adaptive target selection: prefer resources where we are ahead, but ensure we can reach them in time.
    tr = observation.get("turns_remaining", 0)
    rem = observation.get("remaining_resource_count", len(resources))
    time_budget = max(1, tr // 2 + (1 if rem <= 6 else 0))
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        reach_bonus = 6 if myd <= time_budget else -2
        key = ((od - myd) + reach_bonus, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    if best_r is None:
        best_r = resources[0]
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_my = cheb(sx, sy, tx, ty)
    escape_mode = cur_my > max(1, time_budget)

    best_m = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # If in escape mode, prioritize increasing distance from opponent, but still not worsen our resource distance too much.
        if escape_mode:
            dist_from_opp_now = cheb(nx, ny, ox, oy)
            dist_from_opp_cur = cheb(sx, sy, ox, oy)
            score = (dist_from_opp_now - dist_from_opp_cur) * 3 - (myd - cur_my) - neigh_obstacle_penalty(nx, ny)
        else:
            score = (od - myd) * 4 - myd - neigh_obstacle_penalty(nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_m = [dx, dy]

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]
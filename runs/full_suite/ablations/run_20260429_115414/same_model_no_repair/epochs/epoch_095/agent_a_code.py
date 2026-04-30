def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    blocked = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # If on a resource, stay (deterministic).
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    def resource_score(myd, od, rx, ry, step_into_obstacle):
        # Prefer resources where we are closer; otherwise minimize being behind.
        adv = od - myd  # >0 => we are closer
        # Small deterministic obstacle interaction: if resource is near an obstacle, make it slightly less attractive.
        near_obs = 0
        if obstacles:
            for ax, ay in obstacles:
                if cheb(rx, ry, ax, ay) <= 1:
                    near_obs += 1
        # If we would move into obstacle (shouldn't happen), heavily penalize.
        pen = 100 if step_into_obstacle else 0
        # Tuple compares lexicographically: minimize this.
        return (pen, 0 if adv > 0 else 1, -adv if adv > 0 else myd - od, myd + near_obs * 0.1, rx, ry)

    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        into_obst = (nx, ny) in blocked
        if into_obst:
            continue

        # Evaluate by the best target we could pursue from (nx, ny).
        best_res_key = None
        myd_base = None
        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = resource_score(myd, od, rx, ry, False)
            if best_res_key is None or key < best_res_key:
                best_res_key = key
                myd_base = myd

        if best_res_key is None:
            continue

        # Tie-break: prefer moves that reduce our distance to the currently best target.
        # Use lexicographic key to keep deterministic.
        tie = myd_base if myd_base is not None else 0
        move_key = (best_res_key, tie, cheb(nx, ny, ox, oy), dx, dy)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
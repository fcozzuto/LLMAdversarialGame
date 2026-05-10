def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    grid_w, grid_h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def l_shape_blocked(tx, ty):
        # Check both L orders: x-then-y and y-then-x; if either is clear, treat as not blocked.
        def clear_x_then_y():
            x, y = sx, sy
            step_x = 0 if tx == x else (1 if tx > x else -1)
            while x != tx:
                x += step_x
                if (x, y) in obs_set:
                    return False
            step_y = 0 if ty == y else (1 if ty > y else -1)
            while y != ty:
                y += step_y
                if (x, y) in obs_set:
                    return False
            return True

        def clear_y_then_x():
            x, y = sx, sy
            step_y = 0 if ty == y else (1 if ty > y else -1)
            while y != ty:
                y += step_y
                if (x, y) in obs_set:
                    return False
            step_x = 0 if tx == x else (1 if tx > x else -1)
            while x != tx:
                x += step_x
                if (x, y) in obs_set:
                    return False
            return True

        return 1 if (not clear_x_then_y() and not clear_y_then_x()) else 0

    early = observation.get("remaining_resource_count", len(resources)) > max(2, len(resources) // 2)
    best = None
    best_key = None

    for (tx, ty) in resources:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        blocked = l_shape_blocked(tx, ty)
        # Heuristic:
        # - Prefer resources we can reach sooner than opponent (positive (od-sd))
        # - Still keep sd small
        # - If early, strongly contest; if late, prioritize nearest feasible.
        contest = (od - sd)
        if early:
            key = (-contest, blocked, sd, tx, ty)
        else:
            key = (blocked, sd - max(0, contest), sd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If chosen move seems to step into obstacle, try a deterministic safe alternative.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obs_set:
        candidates = [(0, dy), (dx, 0), (0, 0), (dx, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy)]
        for cdx, cdy in candidates:
            xx, yy = sx + cdx, sy + cdy
            if 0 <= xx < grid_w and 0 <= yy < grid_h and (xx, yy) not in obs_set:
                return [cdx, cdy]
        return [0, 0]

    return [dx, dy]
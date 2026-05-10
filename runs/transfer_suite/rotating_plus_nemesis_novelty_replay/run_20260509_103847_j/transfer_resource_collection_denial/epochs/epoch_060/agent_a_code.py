def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_val = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # Evaluate best "contestation" among all resources from next position.
        local_best = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent (do - ds large),
            # then prefer smaller ds, then deterministic resource ordering.
            val = (do - ds, -ds, -rx, -ry)
            if local_best is None or val > local_best:
                local_best = val
        if local_best is None:
            continue

        if best_val is None or local_best > best_val:
            best_val = local_best
            best_move = [dx, dy]

    return best_move
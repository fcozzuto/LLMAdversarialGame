def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_metrics(x, y):
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = abs(x - rx) + abs(y - ry)
            do = abs(ox - rx) + abs(oy - ry)
            # Prefer positions where we have the advantage on a reachable resource,
            # else prefer to approach a resource that opponent is near.
            key = (-(do - ds), ds, -do, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry), ds, do)
        return best

    # If we are already on a resource (possible), take no move.
    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    best_key = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        m = best_metrics(nx, ny)
        if m is None:
            continue
        (key, target, ds, do) = m
        # Add a slight preference for reducing absolute self distance to any resource.
        nearest_d = ds
        tie = (key, nearest_d, -do, nx, ny, dx, dy)
        if best_key is None or tie < best_key:
            best_key = tie
            best_move = [dx, dy]

    # If all moves were blocked, stay.
    return best_move
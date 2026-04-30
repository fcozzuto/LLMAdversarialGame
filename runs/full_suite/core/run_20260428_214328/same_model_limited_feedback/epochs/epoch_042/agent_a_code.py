def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    # If no resources, move toward opponent or away based on distance to avoid collisions
    if not resources:
        tx, ty = ox, oy
    else:
        # Choose nearest resource; break ties by x then y
        def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
        best = None
        for rx, ry in resources:
            d = dist((sx, sy), (rx, ry))
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1]

        # If opponent is closer to the target than we are, pick a different resource
        myd = dist((sx, sy), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        if opd + 1 < myd and len(resources) > 1:
            best2 = None
            for rx, ry in resources:
                myd2 = dist((sx, sy), (rx, ry))
                opd2 = dist((ox, oy), (rx, ry))
                score = (myd2 - opd2, myd2, rx, ry)
                if best2 is None or score < best2[0]:
                    best2 = (score, (rx, ry))
            tx, ty = best2[1]

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                deltas.append((dx, dy))

    resource_set = set(tuple(p) for p in resources)
    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        # Prefer stepping onto a resource
        if (nx, ny) in resource_set:
            return (-10_000, 0, 0, dx, dy)
        # Prefer closeness to target; also slight avoidance of opponent
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        return (d_t, -d_o, nx, ny)

    best_move = None
    best_score = None
    for dx, dy in deltas:
        sc = score_move(dx, dy)
        if best_score is None or sc < best_score:
            best_score = sc
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
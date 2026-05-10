def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best_r = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can secure (ds<=do), otherwise deny best we can.
        key = (0 if ds <= do else 1, ds, -do, rx, ry)
        if best_r is None or key < best_r[0]:
            best_r = (key, (rx, ry))
    tx, ty = best_r[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_to_t = man(nx, ny, tx, ty)
        opp_to_t = man(ox, oy, tx, ty)
        my_to_opp = man(nx, ny, ox, oy)

        # Move to reduce distance to target; if tied, prefer increasing opponent distance.
        # Slightly prefer being closer to target while not walking into obvious opponent pressure.
        key = (my_to_t, opp_to_t - my_to_t, my_to_opp, dx, dy)
        if best_m is None or key < best_m[0]:
            best_m = (key, (dx, dy))

    if best_m is None:
        return [0, 0]
    return [int(best_m[1][0]), int(best_m[1][1])]
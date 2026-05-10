def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    valid = []
    for rx, ry in resources:
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            myd = abs(sx - rx) + abs(sy - ry)
            od = abs(ox - rx) + abs(oy - ry)
            valid.append((rx, ry, myd, od))

    if not valid:
        return [0, 0]

    # Strategic change: prioritize resources where we are strictly closer.
    # If none, choose the one where we are least behind.
    best = None
    for rx, ry, myd, od in valid:
        diff = myd - od  # negative means we are closer
        closer_bonus = 1000 if diff < 0 else 0
        # Tie-break: smaller myd, then closer to center, then lexicographic
        center_bias = -((rx - (w - 1) / 2) ** 2 + (ry - (h - 1) / 2) ** 2)
        key = (closer_bonus - diff, -myd, center_bias, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best[0], best[1], best[2]

    # Choose move that reduces distance to target; if stuck, minimize distance to target anyway.
    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd_next = abs(nx - tx) + abs(ny - ty)

        # Secondary: avoid giving opponent a strong advantage by also considering their distance to the same target.
        od_to_target = abs(ox - tx) + abs(oy - ty)
        my_adv_next = od_to_target - myd_next  # higher is better
        # Tertiary: slight preference to moving closer to opponent when we're already winning overall.
        opp_d = abs(nx - ox) + abs(ny - oy)

        key = (my_adv_next, -myd_next, -opp_d, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move
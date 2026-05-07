def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not valid(sx, sy):
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2 and (valid(r[0], r[1]) or (r[0], r[1]) == (sx, sy))]
    if not res:
        return [0, 0]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate move by the single resource where our advantage is largest
        # Tie-break deterministically by distance and then coordinates.
        best_for_move = None
        for rx, ry in res:
            sd = manhattan(nx, ny, rx, ry)
            od = manhattan(ox, oy, rx, ry)
            margin = od - sd  # bigger => we are closer than opponent
            cand = (margin, -sd, -rx, -ry)
            if best_for_move is None or cand > best_for_move:
                best_for_move = cand
        # Also slightly prefer not moving into positions that are "worse" for all resources
        if best is None or best_for_move > best:
            best = best_for_move
            best_move = [dx, dy]

    return best_move if best is not None else [0, 0]
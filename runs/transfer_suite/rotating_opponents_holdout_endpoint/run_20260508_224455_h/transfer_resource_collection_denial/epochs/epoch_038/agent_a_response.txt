def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def man(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0: d1 = -d1
        d2 = y1 - y2
        if d2 < 0: d2 = -d2
        return d1 + d2

    res_list = [(r[0], r[1]) for r in resources]

    # Pick a resource where we're relatively least behind the opponent (or ahead).
    best_r = None
    best_key = None
    for rx, ry in res_list:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    res_set = set(res_list)

    # Evaluate one-step moves toward the chosen target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        dist_after = man(nx, ny, tx, ty)
        immediate = 1 if (nx, ny) in res_set else 0
        # Prefer reducing distance to target, then immediate collection, then keep from giving up by getting too close to opponent.
        score = (-dist_after, -immediate, man(nx, ny, ox, oy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
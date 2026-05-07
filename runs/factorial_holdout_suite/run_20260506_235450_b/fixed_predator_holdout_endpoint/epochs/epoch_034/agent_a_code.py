def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    turns_remaining = int(observation.get("turns_remaining", 0) or 0)
    late = turns_remaining <= 3

    # Target selection: early prioritize being closer than opponent; late just shortest path for us.
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        if late:
            key = (ds, do)  # minimize our distance, then their distance
        else:
            key = (-(ds - do), ds, do)  # maximize advantage, then closer
        if best_key is None or key < best_key:
            best_key = key
            best_r = [rx, ry]

    rx, ry = best_r
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If a resource is already on our current cell, stay (engine likely handles collection).
    if (sx, sy) in obstacles:
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate move by progress to target plus deterrence of opponent collecting sooner.
        my_d = dist(nx, ny, rx, ry)
        opp_d = dist(ox, oy, rx, ry)

        # Strong bonus if move reaches a resource cell now.
        on_resource = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0

        # Additional slight preference to reduce distance to any resource (helps against deniers).
        nearest_any = 10**9
        for r in resources:
            nearest_any = min(nearest_any, dist(nx, ny, r[0], r[1]))

        # Late game: prioritize actual collection/being on top of resources.
        if late:
            val = (-(on_resource * 1000 + (1 if my_d == 0 else 0) * 500 - my_d), nearest_any)
        else:
            val = (-(on_resource * 1000 + (opp_d - my_d)), my_d, nearest_any)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
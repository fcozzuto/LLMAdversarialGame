def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): nx, ny = sx, sy
            vx = max(abs(nx - ox), abs(ny - oy))
            key = (-vx, nx, ny)  # move lexicographically on tie
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_key = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): nx, ny = sx, sy

        best_for_move = None  # maximize "we are closer than opponent" to same contested target
        for r in resources:
            sd = dist((nx, ny), r)
            od = dist((ox, oy), r)
            # If we can land on a resource now, strongly prioritize it.
            if (nx, ny) == (r[0], r[1]):
                score = 10**9
            else:
                score = (od - sd) * 100 - sd
            key = (-score, sd, od, r[0], r[1])
            if best_for_move is None or key < best_for_move:
                best_for_move = key

        # Overall: maximize best_for_move score => minimize best_for_move key.
        # Tie-break: lexicographically smallest move.
        move_key = (best_for_move[0], best_for_move[1], best_for_move[2], nx, ny, dx, dy)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
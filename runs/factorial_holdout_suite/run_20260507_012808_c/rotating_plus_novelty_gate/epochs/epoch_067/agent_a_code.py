def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    if not resources:
        # If no resources, try to reduce distance to opponent to discourage them (tie-break safe).
        best_key = (-man(sx, sy, ox, oy), sx, sy)
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                key = (-man(nx, ny, ox, oy), nx, ny)
                if key > best_key:
                    best_key = key
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Pick a target resource that we can reach sooner than the opponent.
        local_best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            primary = od - sd  # higher means advantage now
            # Prefer closer resource among equal advantage; deterministic tie-breakers.
            key = (primary, -sd, -rx, -ry)
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue

        # Prefer move with highest local advantage; then smallest self distance to that best resource.
        if best_key is None or local_best > best_key:
            best_key = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
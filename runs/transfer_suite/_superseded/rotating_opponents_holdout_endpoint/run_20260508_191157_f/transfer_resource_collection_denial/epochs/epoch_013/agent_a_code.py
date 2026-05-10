def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_key = None

    # Determine best move by maximizing our lead over opponent for the best remaining resource.
    # Key favors: bigger lead (opp-self), then smaller our distance, then smaller move magnitude, then deterministic tie-break.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        local_best_key = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            lead = od - sd
            # If we can collect sooner (smaller sd), that's good; also break ties toward corner-like deterministic ordering.
            key = (lead, -sd, -(dx * dx + dy * dy), -rx, -ry)
            if local_best_key is None or key > local_best_key:
                local_best_key = key

        if local_best_key is None:
            continue

        if best_key is None or local_best_key > best_key:
            best_key = local_best_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
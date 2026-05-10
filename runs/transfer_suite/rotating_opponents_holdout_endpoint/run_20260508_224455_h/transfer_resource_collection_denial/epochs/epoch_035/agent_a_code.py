def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    res_set = set((p[0], p[1]) for p in resources)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in res_set:
            # Immediate pick is best; still break ties deterministically.
            key = (0, 0, 0, 0, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
            continue

        # Evaluate the best resource we could pursue from the candidate position.
        local_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds  # higher means we are closer than opponent
            # Prefer: larger advantage; then closer to resource; then farther from opponent; then deterministic.
            key2 = (-1 if adv > 0 else 0, -adv, ds, -do, rx * 131 + ry * 17)
            if local_best is None or key2 < local_best:
                local_best = key2

        if local_best is None:
            continue

        # Convert local_best into an ordering key for move selection.
        key = (0, local_best[0], local_best[1], local_best[2], local_best[3], dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that maximize our "next-turn advantage" on a resource.
    # Advantage: (opp distance - 1) - our distance, since opponent can typically reduce by ~1.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        local_best = None
        for rx, ry in resources:
            d_us = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            d_opp_eff = d_opp - 1  # opponent could move closer this turn
            adv = d_opp_eff - d_us

            # Key ranks by highest advantage; then closest our distance; then prefer targets that are farther from opponent
            key = (-adv, d_us, -d_opp, rx, ry)
            if local_best is None or key < local_best:
                local_best = key

        if best is None or local_best < best:
            best = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
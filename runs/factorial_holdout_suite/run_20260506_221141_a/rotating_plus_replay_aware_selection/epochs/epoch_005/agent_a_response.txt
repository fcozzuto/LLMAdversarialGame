def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            dirs.append((dx, dy))
    if not dirs:
        return [0, 0]

    best_move = (0, 0)
    best = None

    # Opponent is nearest_resource-like: bias toward states where we become earlier/safer capturer.
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        cand_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            od = abs(rx - ox) + abs(ry - oy)
            nd = abs(rx - nx) + abs(ry - ny)
            # Higher is better: how much earlier we are than opponent, then arrive sooner, then stable tie-break by coords.
            s1 = od - nd
            s2 = -nd
            s3 = (rx + ry)  # deterministic tie-break
            val = (s1, s2, -s3)
            if (cand_best is None) or (val > cand_best):
                cand_best = val
        # Move-level tie-break: maximize best resource win potential, then minimize our distance to our top resource (implied), then lexicographic.
        if best is None or cand_best > best:
            best = cand_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose a target resource: prefer ones closer to us than opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        d_s = abs(rx - sx) + abs(ry - sy)
        d_o = abs(rx - ox) + abs(ry - oy)
        # Key: maximize opponent disadvantage; then closer to us; then deterministic tie-break.
        key = (d_o - d_s, -d_s, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Evaluate one-step moves.
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            # Prefer moves that don't get rejected; but allow if all blocked.
            continue
        # If we can collect, prioritize it strongly.
        collect = 1 if (nx, ny) == (tx, ty) else 0
        d_s = abs(tx - nx) + abs(ty - ny)
        d_o = abs(tx - ox) + abs(ty - oy)
        # Prefer higher collect, then lower our distance, then higher opponent disadvantage.
        key = (collect, d_o - d_s, -d_s, dx, dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m_key is None:
        # All immediate moves blocked; try to step toward any nearest non-obstacle direction.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [best_m[0], best_m[1]]
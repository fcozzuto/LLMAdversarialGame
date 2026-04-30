def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]
    if not resources:
        return [0, 0]

    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    parity = observation.get("turn_index", 0) % 2

    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        min_us = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            du = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            if du < min_us:
                min_us = du
            if do < min_opp:
                min_opp = do

        # Minimize distance to a good resource; alternate emphasis on "denying" (making resources farther for opponent).
        if parity == 0:
            val = min_us - 0.35 * min_opp
        else:
            val = min_us - 0.10 * min_opp + 0.15 * (abs(nx - ox) + abs(ny - oy))

        if best_val is None or val < best_val - 1e-12 or (abs(val - best_val) <= 1e-12 and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]
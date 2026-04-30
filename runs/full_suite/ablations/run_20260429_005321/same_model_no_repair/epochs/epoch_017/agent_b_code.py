def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    opp = observation.get("opponent_position", [0, 0])
    ox, oy = opp[0], opp[1]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None

    # Precompute resources for deterministic tie-breaking
    res_sorted = sorted(resources, key=lambda p: (p[0], p[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        blocked = (nx, ny) in obs
        # If stepping into obstacle, heavily penalize
        penalty = 1000 if blocked else 0

        # Score: distance to closest reachable resource after this move, with slight push away from opponent
        # (helps prevent getting blocked chasing the same region as opponent)
        min_dist = 10**9
        for rx, ry in res_sorted:
            d = abs(rx - nx) + abs(ry - ny)
            if d < min_dist:
                min_dist = d
        # Opponent pressure: if we're close to a resource they might take, favor moving toward it anyway.
        # Here we just add a small term for being near opponent to reduce collisions/contested paths.
        opp_term = 0
        if ox is not None and oy is not None:
            opp_term = 0.05 * (abs(ox - nx) + abs(oy - ny))

        val = penalty + min_dist + opp_term + 0.001 * (abs(nx - sx) + abs(ny - sy))

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]
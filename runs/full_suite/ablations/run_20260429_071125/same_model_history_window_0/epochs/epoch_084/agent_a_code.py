def choose_move(observation):
    gw = observation["grid_width"]
    gh = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def best_move_for_target(tx, ty, nx, ny):
        ds = dist2(nx, ny, tx, ty)
        do = dist2(ox, oy, tx, ty)
        return (do - ds) - 0.05 * ds

    best_score = None
    best_delta = [0, 0]

    if not resources:
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh:
            continue
        if (nx, ny) in obstacles:
            continue
        score = -10**18
        for rx, ry in resources:
            v = best_move_for_target(rx, ry, nx, ny)
            if v > score:
                score = v
        if best_score is None or score > best_score:
            best_score = score
            best_delta = [dx, dy]

    return [best_delta[0], best_delta[1]]
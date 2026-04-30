def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)
    resources = observation.get("resources", [])
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-direction movement

    # If standing on obstacle (shouldn't happen), stay safe
    if (sx, sy) in obs_set:
        return [0, 0]

    if resources:
        # Choose best target: prefer resources where we are closer than opponent, then nearer overall.
        best_res = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            d_s = dist((sx, sy), (rx, ry))
            d_o = dist((ox, oy), (rx, ry))
            # Key: maximize advantage (opp - self), then minimize our distance, then deterministic tie-break.
            key = (d_o - d_s, -d_s, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        # No visible resources: go to center
        tx, ty = (w // 2), (h // 2)

    # Pick move that best improves our approach to target while keeping away from opponent's reach to it.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        d_s = dist((nx, ny), (tx, ty))
        d_o = dist((ox, oy), (tx, ty))
        # Score: minimize our distance, maximize our advantage over opponent (including on next move), deterministic tie-break.
        advantage = d_o - d_s
        key = (-d_s, advantage, -abs(nx - (w // 2)) - abs(ny - (h // 2)), -dx, -dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
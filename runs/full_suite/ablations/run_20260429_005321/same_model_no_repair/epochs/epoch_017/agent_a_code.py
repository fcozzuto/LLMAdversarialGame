def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        return [dx, dy]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # distance to closest resource after move
        mind = 10**9
        for rx, ry in resources:
            d = abs(rx - nx) + abs(ry - ny)
            if d < mind:
                mind = d

        # softly avoid giving opponent easy path: prefer positions farther from opponent
        oppd = abs(ox - nx) + abs(oy - ny)

        # also bias toward resources roughly in our direction (reduces dithering)
        dir_bias = 0
        for rx, ry in resources:
            if abs(rx - nx) + abs(ry - ny) == mind:
                dir_bias = (1 if (rx - nx) * (ox - nx) <= 0 else 0) + (1 if (ry - ny) * (oy - ny) <= 0 else 0)
                break

        val = -mind + 0.15 * oppd + 0.05 * dir_bias
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
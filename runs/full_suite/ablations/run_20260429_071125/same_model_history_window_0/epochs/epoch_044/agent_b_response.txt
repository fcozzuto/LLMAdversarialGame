def choose_move(observation):
    grid_w = observation["grid_width"]
    grid_h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**9

    res_set = set((x, y) for x, y in resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= grid_w or ny < 0 or ny >= grid_h:
            continue
        if (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in res_set:
            base += 1000

        d_opp = dist((nx, ny), (ox, oy))
        base -= 0.2 * d_opp

        best_res = -10**9
        for rx, ry in resources:
            d_me = dist((nx, ny), (rx, ry))
            d_op = dist((ox, oy), (rx, ry))
            # Prefer resources where we are closer than opponent
            val = (d_op - d_me) - 0.05 * d_me
            if val > best_res:
                best_res = val

        score = base + best_res
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
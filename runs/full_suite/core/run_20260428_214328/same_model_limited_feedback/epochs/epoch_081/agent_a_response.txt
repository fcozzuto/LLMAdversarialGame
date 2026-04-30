def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    if not resources:
        return [0, 0]

    def sqdist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    def best_target():
        best = None
        best_cost = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = sqdist((sx, sy), (rx, ry))
            od = sqdist((ox, oy), (rx, ry))
            cost = sd - 0.35 * od
            if best is None or cost < best_cost or (cost == best_cost and (rx, ry) < best):
                best = (rx, ry)
                best_cost = cost
        return best

    tx, ty = best_target()

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        score = sqdist((nx, ny), (tx, ty)) - 0.15 * sqdist((ox, oy), (tx, ty))
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
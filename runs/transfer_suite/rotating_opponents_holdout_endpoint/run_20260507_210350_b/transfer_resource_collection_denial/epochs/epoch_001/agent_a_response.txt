def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy)

    # Choose closest remaining resource; tie-break deterministically by coordinates
    if resources:
        candidates = []
        for r in resources:
            if r not in obstacles:
                candidates.append((dist((x, y), r), r[0], r[1], r))
        candidates.sort()
        target = candidates[0][3]
    else:
        target = (observation["grid_width"] // 2, observation["grid_height"] // 2)

    # Greedy move toward target with obstacle avoidance
    tx, ty = target
    best = (10**9, 0, 0)  # (score, newx, newy)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"]):
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), target)
        # Small bias: prefer moves that don't allow the opponent to immediately take the same resource
        opp_d = dist((ox, oy), target)
        my_gain = opp_d - d
        score = d * 10 - my_gain
        if score < best[0] or (score == best[0] and (nx, ny) < (best[1], best[2])):
            best = (score, nx, ny)

    return [best[1] - x, best[2] - y]
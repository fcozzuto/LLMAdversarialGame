def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set((x, y) for x, y in obstacles)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_to_opp = dist((sx, sy), (ox, oy))

    if resources:
        best_target = None
        best_key = None
        for rx, ry in resources:
            ks = dist((sx, sy), (rx, ry))
            ko = dist((ox, oy), (rx, ry))
            key = (ks + 0.35 * ko, ks, -ko, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_target = (rx, ry)
        tx, ty = best_target
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs_set:
            continue

        nd_to_target = dist((nx, ny), (tx, ty))
        score = 0.0

        if resources:
            score += -2.2 * nd_to_target
            # Prefer being the closer pursuer to the best few resources
            for rx, ry in resources[:min(4, len(resources))]:
                d1 = dist((nx, ny), (rx, ry))
                d2 = dist((ox, oy), (rx, ry))
                score += 0.35 * (d2 - d1)
        else:
            score += -0.15 * dist((nx, ny), (tx, ty))

        nd_to_opp = dist((nx, ny), (ox, oy))
        if nd_to_opp <= 1:
            score -= 2.5
        # Mild bias toward reducing distance to opponent to prevent them from freely collecting
        score += 0.08 * (cur_to_opp - nd_to_opp)

        # Tie-break deterministically by preferring lower dx, then dy, then lower position
        key = (-score, dx, dy, nx, ny)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
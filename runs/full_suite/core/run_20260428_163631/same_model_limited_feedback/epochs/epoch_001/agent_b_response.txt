def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = [tuple(p) for p in observation.get("resources", [])]
    w, h = observation["grid_width"], observation["grid_height"]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda m: (m[0], m[1]))

    if resources:
        best = None
        for r in resources:
            d_self = dist((x, y), r)
            d_opp = dist((ox, oy), r)
            score = d_opp - d_self  # prefer resources closer to self than opponent
            tie = (-score, r[0], r[1])
            if best is None or tie < best[0]:
                best = (tie, r)
        target = best[1]
    else:
        target = (w // 2, h // 2)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        v = dist((nx, ny), target)
        # slight repulsion from opponent to reduce contention
        v += 0.1 * dist((nx, ny), (ox, oy))
        if best_val is None or v < best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
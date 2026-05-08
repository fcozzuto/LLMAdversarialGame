def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    if (sx, sy) in obs:
        return [0, 0]

    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    res = [(r[0], r[1]) for r in resources if len(r) >= 2 and inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    best_t = None
    best_key = None
    for rx, ry in res:
        dself = dist((sx, sy), (rx, ry))
        dopp = dist((ox, oy), (rx, ry))
        key = (dopp - dself, -dself)  # want we are closer than opponent; then closer overall
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dnew = dist((nx, ny), (rx, ry))
        score = (dnew, -(best_key[0]))  # minimize distance to target
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
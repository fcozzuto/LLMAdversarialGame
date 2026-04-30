def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    if not resources:
        return [0, 0]

    def king_dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best_score = None
    best_target = resources[0]
    for rx, ry in resources:
        ds = king_dist((sx, sy), (rx, ry))
        do = king_dist((ox, oy), (rx, ry))
        score = 2 * ds - do  # prefer resources we reach sooner than opponent
        if best_score is None or score < best_score or (score == best_score and ds < king_dist((sx, sy), best_target)):
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_util = None
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        new_d = king_dist((nx, ny), (tx, ty))
        cur_d = king_dist((sx, sy), (tx, ty))
        util = -new_d
        if new_d < cur_d:
            util += 0.25
        # small tie-break: also drift away if opponent would land on same square next step
        if king_dist((nx, ny), (ox, oy)) <= 0:
            util -= 0.5
        if best_util is None or util > best_util:
            best_util = util
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
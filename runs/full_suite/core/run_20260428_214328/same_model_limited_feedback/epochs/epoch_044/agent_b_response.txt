def choose_move(observation):
    W, H = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # No resources known: drift to center while avoiding obstacles
        tx, ty = W // 2, H // 2
        best_step = (0, 0)
        best_d = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= W or ny < 0 or ny >= H or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < best_d or (d == best_d and (dx, dy) < best_step):
                best_d, best_step = d, (dx, dy)
        return [best_step[0], best_step[1]]

    # Pick a resource where we are relatively closer than the opponent.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = (do - ds) * 1000 - ds  # prioritize advantage, then closeness
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    # Choose a legal move that minimizes distance to target; if tied, prefer blocking opponent by increasing their distance.
    best_step = (0, 0)
    best_d = 10**9
    best_block = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H or (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        block = dist((ox, oy), (tx, ty)) - dist((ox, oy), (tx, ty))  # always 0, kept for determinism if extended
        if d < best_d or (d == best_d and block > best_block) or (d == best_d and block == best_block and (dx, dy) < best_step):
            best_d = d
            best_block = block
            best_step = (dx, dy)

    return [best_step[0], best_step[1]]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
                continue
            score = dist(nx, ny, ox, oy)  # drift away
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue

        # Choose resource where we are relatively closer than opponent
        candidate = None
        candidate_val = -10**18
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Favor resources we can secure sooner; penalize ones opponent is closer to
            val = 0.5 * do - 1.5 * ds - 0.05 * abs((rx - ox) - (ry - oy))
            if val > candidate_val:
                candidate_val = val
                candidate = (rx, ry)

        # Small bonus if moving toward any nearby resource and reducing distance to opponent's best pick
        immediate = 0
        if candidate is not None:
            immediate = -dist(nx, ny, candidate[0], candidate[1])

        # Prefer advancing (avoid dithering) while staying safe
        step_adv = -dist(nx, ny, 0, 0) * 0.0 + 0.0  # deterministic neutral placeholder

        score = candidate_val + immediate + step_adv + (0.01 if (nx, ny) in obstacles else 0)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
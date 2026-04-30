def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs_set = set((a, b) for a, b in obstacles)

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_primary = -10**9
    best_tiebreak = 10**9

    if not resources:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs_set:
            continue
        # Choose resource that gives maximum advantage (opponent distance - our distance)
        primary = -10**9
        tiebreak = 10**9
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > primary or (adv == primary and ds < tiebreak):
                primary = adv
                tiebreak = ds
        if primary > best_primary or (primary == best_primary and tiebreak < best_tiebreak):
            best_primary = primary
            best_tiebreak = tiebreak
            best_move = (dx, dy)

    # If all moves were blocked, stay
    if best_move == (0, 0):
        return [0, 0]
    return [best_move[0], best_move[1]]
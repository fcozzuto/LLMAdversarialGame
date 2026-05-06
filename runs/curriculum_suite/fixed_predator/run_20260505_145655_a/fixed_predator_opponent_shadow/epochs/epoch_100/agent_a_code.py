def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_move = [0, 0]
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny) or (nx, ny) in blocked:
                continue
            s = 0
            for rx, ry in resources:
                dm = abs(nx - rx) + abs(ny - ry)
                do = abs(ox - rx) + abs(oy - ry)
                diff = do - dm
                # Favor resources where we can arrive no later than opponent, also prefer closer ones.
                s += (diff * 1000) - dm
            if s > best_score:
                best_score = s
                best_move = [dx, dy]
        return best_move

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue
        myd = abs(nx - ox) + abs(ny - oy)
        score = myd
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move
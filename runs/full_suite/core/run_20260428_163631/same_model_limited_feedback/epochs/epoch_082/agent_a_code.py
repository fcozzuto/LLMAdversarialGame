def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    mx, my = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = mx + dx, my + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        val = -10**18
        for rx, ry in resources:
            md = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            v = -md - 0.6 * od
            if v > val:
                val = v
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (-(10**9), 10**9, 0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        local_best = -(10**9)
        local_best_d = 10**9
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            rel = opp_d - self_d  # positive means we are closer than opponent
            if rel > local_best or (rel == local_best and self_d < local_best_d):
                local_best = rel
                local_best_d = self_d
        cand = (-(local_best), local_best_d, dx, dy)
        if cand < (best_move[0], best_move[1], best_move[2], best_move[3]):
            best_move = (cand[0], cand[1], dx, dy)

    # If blocked on all non-obstacle moves, allow staying within bounds even if obstacle (engine will keep in place)
    if best_move[0] == -(10**9):
        best_move = (0, 10**9, 0, 0)

    return [best_move[2], best_move[3]]
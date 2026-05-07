def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # Evaluate move by the best resource we can target next.
        move_best = None
        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            op_d = man(ox, oy, rx, ry)
            # Primary: how much closer we are than opponent (or how quickly we reduce deficit)
            # Secondary: prefer closer resources and avoid "stupid" far moves.
            val = (op_d - my_d) * 100 - my_d * 3
            if move_best is None or val > move_best:
                move_best = val

        # Tertiary: slight preference to approach opponent if resources are contested
        contest_pressure = 0
        for rx, ry in resources:
            if man(sx, sy, rx, ry) - man(ox, oy, rx, ry) < 0:
                contest_pressure = 1
                break
        if contest_pressure:
            move_score = move_best - man(nx, ny, ox, oy)
        else:
            move_score = move_best

        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]

    return best_move
def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # If an immediate resource is available, grab it deterministically.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            for rx, ry in resources:
                if (rx, ry) == (nx, ny):
                    return [dx, dy]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate this move by looking for the best resource we can contest.
        move_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer being closer than opponent; otherwise race for closest.
            contest = od - sd
            if sd == 0:
                val = 10**6
            else:
                # When we are behind, prioritize reducing our distance; when tied/ahead, prioritize margin.
                val = (1000 if sd <= od else 0) + contest * 5 - sd * 0.5 + (0.001 if sd == od else 0.0)
            if val > move_best:
                move_best = val
        if move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
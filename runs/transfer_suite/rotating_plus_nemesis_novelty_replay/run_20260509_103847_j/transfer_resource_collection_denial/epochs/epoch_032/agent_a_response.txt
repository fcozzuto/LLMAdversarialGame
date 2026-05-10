def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    ts = observation.get("turns_remaining", 0)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = None

    # Heuristic: maximize winning contest on the most favorable reachable resource,
    # while discouraging paths that increase distance to all resources.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue

        # Consider current move's best "take-first" opportunity.
        move_best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Primary: who reaches sooner (difference), Secondary: prefer nearer targets (smaller sd),
            # Tertiary: prefer resources that likely remain (sd close to ts).
            # Clamp sd by ts so far-away targets don't mislead.
            time_factor = (ts - sd)
            key = (od - sd, -sd, time_factor, rx, ry)
            if move_best is None or key > move_best:
                move_best = key

        if move_best is None:
            continue

        # Additional penalty if we don't improve our distance to any good target.
        # Compare best key for current position (deterministic extra lookahead).
        cur_best = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            key = (od - sd, -sd, ts - sd, rx, ry)
            if cur_best is None or key > cur_best:
                cur_best = key

        improvement = 0
        if cur_best is not None:
            improvement = (move_best[0] - cur_best[0]) + (move_best[1] - cur_best[1]) * 0.1

        # Final score ordering.
        score = (move_best[0], move_best[1], move_best[2], improvement, -dx*dx - dy*dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
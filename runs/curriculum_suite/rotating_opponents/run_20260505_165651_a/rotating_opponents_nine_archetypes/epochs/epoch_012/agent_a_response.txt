def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose best next cell by greedily maximizing a race-and-greed score over resources.
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # If we step onto a resource, heavily prioritize.
        here_res = (nx, ny) in set(tuple(r) for r in resources)
        my_best = 10**9
        opp_best = 10**9
        best_race = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            race = (od - sd)
            center_pen = 0.02 * (abs(rx - cx) + abs(ry - cy))
            greed = 0.8 / (sd + 1)
            if race + greed - center_pen > best_race:
                best_race = race + greed - center_pen
                my_best = sd
                opp_best = od
        # Prefer immediate collection, then win the closest race (opp far / we near), then reduce distance.
        score = (2000 if here_res else 0) + best_race + 0.05 * (opp_best - my_best) - 0.01 * (my_best)
        tie = (-(dx), -(dy), nx, ny)
        cand = (score, tie[0], tie[1])
        if cand > best:
            best = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
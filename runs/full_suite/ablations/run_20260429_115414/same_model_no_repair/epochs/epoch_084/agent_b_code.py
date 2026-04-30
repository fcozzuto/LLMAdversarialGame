def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obs_set = {(p[0], p[1]) for p in obstacles}
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs_set:
            continue
        val = None
        for r in resources:
            our_d = abs(r[0] - nx) + abs(r[1] - ny)
            opp_d = abs(r[0] - ox) + abs(r[1] - oy)
            util = (opp_d - our_d) * 3 - our_d
            if val is None or util > val:
                val = util
        if val is None:
            continue
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # tie-break: prefer smaller our distance to the closest valuable resource
            cur_best_dist = min(manhattan((sx + best_move[0], sy + best_move[1]), r) for r in resources)
            new_dist = min(manhattan((nx, ny), r) for r in resources)
            if new_dist < cur_best_dist:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**18, 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        cur_best = -10**18
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            if self_d == 0:
                benefit = 10**9
            else:
                benefit = opp_d - self_d  # positive: we are closer
                benefit -= 0.01 * self_d  # prefer shorter after benefit tie

            # Combine: prioritize securing/denying (benefit), then fast collection (low self_d)
            score = benefit * 1000 - self_d
            if score > cur_best:
                cur_best = score

        # Tie-break deterministically toward moves closer to overall nearest resource
        if cur_best > best_move[0]:
            best_move = (cur_best, dx, dy)

    return [int(best_move[1]), int(best_move[2])]
def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    valid_res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obstacles]
    if not valid_res:
        return [0, 0]

    def man(ax, ay, bx, by):
        v = ax - bx
        if v < 0:
            v = -v
        u = ay - by
        if u < 0:
            u = -u
        return v + u

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    rem = observation.get("remaining_resource_count", len(valid_res))
    turns = observation.get("turns_remaining", 1)
    threat_weight = 1.0 + (rem / 12.0)
    time_weight = 0.02 * (turns % 7)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Choose the resource where we gain the most advantage next, but add a small time bias.
        local_best_adv = -10**18
        local_best_selfd = 10**18
        for rx, ry in valid_res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = (od - sd) * threat_weight - time_weight * sd
            if adv > local_best_adv or (adv == local_best_adv and sd < local_best_selfd):
                local_best_adv = adv
                local_best_selfd = sd

        # If we can't get strong advantage anywhere, move to the closest resource; otherwise maximize advantage.
        fallback_sd = min(man(nx, ny, rx, ry) for (rx, ry) in valid_res)
        fallback_score = -fallback_sd

        if local_best_adv < 0:
            move_score = fallback_score
        else:
            move_score = local_best_adv * 1000 - local_best_selfd

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
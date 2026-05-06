def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best_val = -10**18
    best_move = (0, 0)
    best_secondary = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue

        local_best = -10**18
        local_pick_dist = 10**18
        for rx, ry in resources:
            d1 = man(nx, ny, rx, ry)   # self
            d2 = man(ox, oy, rx, ry)   # opponent
            # Want denial/contesting: maximize (opponent later - us earlier) and when equal, prefer closer to us.
            val = (d2 - d1) * 10 - d1
            if val > local_best or (val == local_best and d1 < local_pick_dist):
                local_best = val
                local_pick_dist = d1

        # Additional pressure: if we can reduce opponent's immediate access, slightly prefer it.
        opp_to_self_move = man(nx, ny, ox, oy)
        # Prefer moves that keep us near the contested target (tie-breaker).
        secondary = local_pick_dist + (opp_to_self_move // 2)

        if local_best > best_val or (local_best == best_val and secondary < best_secondary):
            best_val = local_best
            best_secondary = secondary
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
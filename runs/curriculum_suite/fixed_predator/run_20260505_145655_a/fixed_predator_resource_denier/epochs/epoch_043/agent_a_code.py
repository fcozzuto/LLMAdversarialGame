def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    best_move = [0, 0]
    best_val = -10**18

    # Deterministic ordering for tie-breaks
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Value: prioritize resources we can reach no later than opponent, then deny high-value targets.
        local_best = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            margin = oppd - selfd  # positive => we are closer
            # If we can win it, strongly prefer; otherwise still prefer least loss and proximity.
            win_term = margin * 10
            deny_term = -max(0, -margin) * 6
            dist_term = -selfd * 1.2
            # Encourage disrupting nearby opponent by moving toward their likely targets slightly.
            opp_close = -((abs(nx - ox) + abs(ny - oy)) * 0.03)
            val = win_term + deny_term + dist_term + opp_close
            if val > local_best:
                local_best = val

        if local_best > best_val:
            best_val = local_best
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
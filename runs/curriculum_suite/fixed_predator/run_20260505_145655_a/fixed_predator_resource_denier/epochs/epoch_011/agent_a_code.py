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
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Evaluate one-step action by best attainable "out-approach" advantage.
    # Also include a mild "interceptor" term: if opponent is close, prefer moves that
    # reduce the distance to opponent slightly (denies tempo).
    best_move = (0, 0)
    best_val = -10**18

    opp_dist = abs(sx - ox) + abs(sy - oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Interceptor: if opponent is close, moving toward them can prevent quick grabs.
        # Deterministic small weight.
        interceptor = 0
        if opp_dist <= 4:
            interceptor = (opp_dist - (abs(nx - ox) + abs(ny - oy))) * 0.6

        # Prefer resources where we are (or will be) closer than opponent.
        local_best = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            advantage = (oppd - selfd)  # positive => we are closer
            # Encourage grabbing soon (smaller selfd) and beating opponent.
            # If we can't win a resource immediately, still choose the action that maximizes
            # the gap to deny their timing.
            val = advantage * 7 - selfd * 0.8
            if val > local_best:
                local_best = val

        total = local_best + interceptor

        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
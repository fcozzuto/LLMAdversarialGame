def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rp = (p[0], p[1])
            if rp not in obstacles:
                resources.append(rp)
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Contested targeting with one-step "steal then deny" flavor.
    best_move = (0, 0)
    best_val = -10**30

    # Slight tie-breaking: prefer moves that reduce our distance to the best global resource.
    global_best_r = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
    global_best_d = man(sx, sy, global_best_r[0], global_best_r[1])

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # If we step onto a resource, heavily prioritize.
        step_best = -10**30
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)

            # Positive when we're closer than opponent; strong incentive to secure/beat them.
            # Deny term: if opponent is also close, we want to reduce our future too.
            # When ds==0, it dominates.
            val = (do - ds) * 5000 - ds * 20
            if ds == 0:
                val += 10**9
            step_best = max(step_best, val)

        # Deny additional: prefer moves that pull us closer to the opponent while going for best target
        # (helps in shadow archetype where they pressure mid-map).
        opp_c = man(nx, ny, ox, oy)
        global_d_after = man(nx, ny, global_best_r[0], global_best_r[1])

        # Combine with deterministic tie-breaks.
        v = step_best - opp_c * 2 - global_d_after * 1 + (1 if global_best_d > global_d_after else 0)

        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
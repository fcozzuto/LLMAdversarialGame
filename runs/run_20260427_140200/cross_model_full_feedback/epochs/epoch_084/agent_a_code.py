def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    center = (w // 2, h // 2)

    # Evaluate moves by choosing a resource where we can gain an immediate distance advantage.
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not in_bounds(nx, ny):
            continue

        # If stepping onto a resource, strongly prefer it.
        onto_res = 0
        for (rx, ry) in resources:
            if rx == nx and ry == ny:
                onto_res = 1
                break

        # Prefer moving to a target where (opponent distance - our distance) is maximized after the move.
        adv_best = -10**9
        dist_best = 10**9
        for (rx, ry) in resources:
            d_me = man((nx, ny), (rx, ry))
            d_opp = man((ox, oy), (rx, ry))
            adv = d_opp - d_me
            if adv > adv_best:
                adv_best = adv
                dist_best = d_me

        # If no resources, drift to center and away from being stuck next to obstacles.
        if not resources:
            adv_best = -man((nx, ny), center)
            dist_best = 0

        # Also lightly avoid getting closer to opponent only when we can't secure a resource quickly.
        close_to_opp = man((nx, ny), (ox, oy))

        val = 0
        val += onto_res * 10**6
        val += adv_best * 200
        val += (-dist_best) * 5
        if not resources:
            val += -close_to_opp * 1
        else:
            # If our advantage is not positive, try to reduce opponent access by moving away from the opponent.
            if adv_best < 0:
                val += -close_to_opp * 3

        # Deterministic tie-breaker: prefer staying still last? We'll prefer smaller dx,dy magnitude then lexicographic.
        if val > best_val or (val == best_val and (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
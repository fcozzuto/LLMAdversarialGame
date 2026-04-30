def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource we can beat the opponent on
    if resources:
        best_t = resources[0]
        best_comp = -10**18
        for t in resources:
            sd = dist((sx, sy), t)
            od = dist((ox, oy), t)
            comp = od - sd
            if comp > best_comp or (comp == best_comp and (sd < dist((sx, sy), best_t))):
                best_comp = comp
                best_t = t
        tx, ty = best_t
    else:
        tx, ty = (w - 1, h - 1)

    best = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        our_d = dist((nx, ny), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))
        # Primary: reduce our distance; Secondary: keep/expand advantage; Tertiary: avoid getting closer to obstacles not needed
        score = (-our_d * 100) + ((opp_d - our_d) * 10)
        if resources:
            # If multiple resources, slightly bias toward the best-for-us among the next step
            step_best = -10**18
            for t in resources:
                sd = dist((nx, ny), t)
                od = dist((ox, oy), t)
                c = od - sd
                if c > step_best:
                    step_best = c
            score += step_best
        # Deterministic tie-break: prefer staying still, then lexicographic deltas
        if score > best_score or (score == best_score and ((dx, dy) == (0, 0) or (dx, dy) < best)):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
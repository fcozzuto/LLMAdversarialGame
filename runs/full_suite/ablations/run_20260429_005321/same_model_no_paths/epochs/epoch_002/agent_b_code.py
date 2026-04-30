def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2
        return pen

    # Choose a target that maximizes our potential advantage over opponent right now
    if resources:
        best_r = None
        best_adv = -10**18
        for r in resources:
            myd = md((sx, sy), r)
            opd = md((ox, oy), r)
            adv = opd - myd
            key = (adv, -myd, -r[0], -r[1])
            if best_r is None or key > best_adv:
                best_adv = key
                best_r = r
        tx, ty = best_r
    else:
        # No resources known: head to center of remaining map and also slightly deny by drifting toward opponent's line
        tx, ty = (w - 1) // 2, (h - 1) // 2
        if resources == []:
            # deterministic tie: if opponent closer to our corner, move toward them
            if md((sx, sy), (0, 0)) < md((ox, oy), (0, 0)):
                tx, ty = ox, oy

    best_move = (0, 0)
    best_score = -10**18
    # One-step lookahead: maximize (opponent distance - my distance) to target after my move, plus obstacle avoidance
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        pen = obs_pen(nx, ny)
        if pen >= 10**8:
            continue
        myd = md((nx, ny), (tx, ty))
        opd = md((ox, oy), (tx, ty))
        adv_after = opd - myd  # positive = I'm closer than opponent at this step
        # small preference for reducing my distance (stability) and not getting too close to opponent (avoid accidental commitment)
        score = adv_after * 100 - myd - 2 * md((nx, ny), (ox, oy)) - pen
        # deterministic tie-break by move order
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
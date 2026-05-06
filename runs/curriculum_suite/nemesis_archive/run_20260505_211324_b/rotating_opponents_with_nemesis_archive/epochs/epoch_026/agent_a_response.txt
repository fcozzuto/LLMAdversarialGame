def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (0, 0)
    best_score = -10**9
    # Favor advancing y while contesting resources that opponent is NOT about to take.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Lightweight "sweep_rows" counter: if opponent is close to a resource row, avoid
        # moving into that row unless we can beat their distance there.
        move_score = 0
        move_penalty = 0

        # Prefer progress upward unless blocked.
        move_score += (ny - sy) * 1.3

        for (rx, ry) in res:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            # Advantage toward this resource.
            adv = (od - sd)
            # If opponent is close on that row y, discourage unless we are actually better.
            row_closeness = abs(ry - oy)
            row_pen = 0.0
            if row_closeness <= 1:
                if adv < 1:
                    row_pen = 3.0
                else:
                    row_pen = 0.5
            # Also slightly prefer resources on our side (lower x) when opponent is sweeping leftwards.
            side_bonus = 0.0
            if ox > (w - 1) / 2 and rx <= (w - 1) / 2:
                side_bonus = 0.4

            # Combine: closer and winning the contest is best.
            value = adv * 2.2 - sd * 0.35 + side_bonus - row_pen
            # Small reward for immediate reach/near reach.
            if sd == 0:
                value += 8.0
            elif sd == 1:
                value += 2.0

            move_score += value
            move_penalty += 0.02 * sd

        move_score -= move_penalty
        if move_score > best_score:
            best_score = move_score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
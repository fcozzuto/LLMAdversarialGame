def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Deterministic drift: move toward the corner farthest from opponent.
        tx, ty = (0, 0)
        if (w - 1 - ox) + (h - 1 - oy) > ox + oy:
            tx, ty = (w - 1, h - 1)
        elif (w - 1 - ox) + oy > ox + (h - 1 - oy):
            tx, ty = (w - 1, 0)
        elif ox + (h - 1 - oy) > ox + oy:
            tx, ty = (0, h - 1)
        else:
            tx, ty = (0, 0)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a resource we are comparatively closer to than the opponent (stronger self preference).
    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Lower is better: prefer resources where we have a clear distance advantage.
        urgency = sd - 1.25 * od
        # Tie-break deterministically: prefer immediate, then smaller sd.
        key = (urgency, sd, -od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), sd, od)

    if best is None:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [-dx, -dy]

    (key, (rx, ry), _, _) = best
    if (sx, sy) == (rx, ry) or (sx, sy) in resources:
        return [0, 0]

    # Evaluate one-step moves by resulting distance advantage to chosen resource.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = man(nx, ny, rx, ry)
        od2 = man(ox, oy, rx, ry)
        # Encourage capturing sooner; discourage moves that allow opponent advantage to rise.
        score = (sd2, sd2 - od2, abs(nx - rx) + abs(ny - ry), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
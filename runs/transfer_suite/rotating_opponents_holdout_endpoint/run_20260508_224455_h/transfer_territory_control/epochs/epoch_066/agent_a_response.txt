def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])

    def to_set(obj):
        s = set()
        for c in obj or []:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                s.add((int(c[0]), int(c[1])))
        return s

    un = to_set(observation.get("unclaimed_cells"))
    myt = to_set(observation.get("self_territory"))
    opt = to_set(observation.get("opponent_territory"))
    obst = to_set(observation.get("obstacles"))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose a strategic target: nearest unclaimed cell adjacent to opponent territory, else nearest unclaimed toward opponent, else toward center.
    target = None
    frontier = []
    for (x, y) in un:
        if (x - 1, y) in opt or (x + 1, y) in opt or (x, y - 1) in opt or (x, y + 1) in opt:
            frontier.append((x, y))
    if frontier:
        target = min(frontier, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), abs(t[0] - ox) + abs(t[1] - oy), t[0], t[1]))
    elif un:
        target = min(un, key=lambda t: (abs(t[0] - ox) + abs(t[1] - oy), abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        target = (int(round(cx)), int(round(cy)))

    tx, ty = target
    # Deterministic neighbor evaluation (avoids obstacles if possible).
    best = None
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        cell = (nx, ny)
        dist_t = abs(tx - nx) + abs(ty - ny)
        # Prefer entering opponent territory, then unclaimed adjacent/frontier, then unclaimed, then self territory.
        if cell in opt:
            score = 100000 - dist_t
        elif cell in un:
            adj_opp = ((nx - 1, ny) in opt) or ((nx + 1, ny) in opt) or ((nx, ny - 1) in opt) or ((nx, ny + 1) in opt)
            score = (50000 if adj_opp else 1000) - dist_t
        elif cell in myt:
            score = 200 - dist_t
        else:
            score = 0 - dist_t
        # Nudge toward increasing control by discouraging stepping onto non-useful empty/unclaimed away from target.
        if cell not in un and cell not in opt and cell not in myt:
            score -= 50
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is not None:
        return [int(best[0]), int(best[1])]

    # If all non-obstacle moves were invalid (rare), allow staying.
    return [0, 0]
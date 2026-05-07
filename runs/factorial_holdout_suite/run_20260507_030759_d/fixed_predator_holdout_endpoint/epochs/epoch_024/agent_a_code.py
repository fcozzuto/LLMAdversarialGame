def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    ox, oy = observation["opponent_position"]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def travel(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev (diagonal allowed)

    if not resources:
        cx, cy = w // 2, h // 2
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    best = None  # (advantage, self_time, -resource_count_at_bestcell, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        local_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = travel(nx, ny, rx, ry)
            ot = travel(ox, oy, rx, ry)
            adv = ot - st
            # Prefer guaranteed or near-certain grabs; then prefer faster.
            cand = (adv, st, -((rx, ry) == (nx, ny)), rx, ry)
            if local_best is None or cand > local_best:
                local_best = cand

        if local_best is None:
            continue
        adv, st = local_best[0], local_best[1]
        key = (adv, st, -sum(1 for (rx, ry) in resources if (rx, ry) == (nx, ny)), dx, dy)
        if best is None or key > best:
            best = key

    return [best[3], best[4]] if best is not None else [0, 0]
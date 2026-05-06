def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    best = None
    k = 0.35
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_to_opp = man(nx, ny, ox, oy)
        # Choose move that targets resources where we have relative advantage over opponent.
        best_metric = None
        for rx, ry in resources:
            d1 = man(nx, ny, rx, ry)
            d2 = man(ox, oy, rx, ry)
            metric = d1 - k * d2
            if best_metric is None or metric < best_metric:
                best_metric = metric
        # Mild preference: don't allow getting too close to opponent (reduces contention/collisions).
        score = (best_metric, -my_to_opp, abs(dx) + abs(dy), dx, dy)
        if best is None or score < best:
            best = score

    return [best[3], best[4]] if best is not None else [0, 0]
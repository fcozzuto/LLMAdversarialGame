def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (score, dx, dy)

    # Denial if opponent is closer to the closest resource to us.
    my_best = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < my_best:
            my_best = d
    denial = False
    for rx, ry in resources:
        if cheb(sx, sy, rx, ry) == my_best and cheb(ox, oy, rx, ry) < my_best:
            denial = True
            break

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        if denial:
            # Try to increase opponent distance to any resource while keeping ours not too bad.
            s = -10**9
            for rx, ry in resources:
                opd = cheb(ox, oy, rx, ry)
                myd = cheb(nx, ny, rx, ry)
                s = max(s, (opd - myd) - myd * 0.01)
        else:
            # Greedy maximize our closeness improvement to the nearest resource.
            s = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                s = max(s, -myd - cheb(ox, oy, rx, ry) * 0.001)

        if best is None or s > best[0]:
            best = (s, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]
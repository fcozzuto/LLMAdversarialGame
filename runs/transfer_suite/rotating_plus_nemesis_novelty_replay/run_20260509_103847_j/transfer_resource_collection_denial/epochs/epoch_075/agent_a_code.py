def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    raw_resources = observation.get("resources") or []
    resources = []
    for p in raw_resources:
        try:
            x, y = p
        except Exception:
            x, y = p[0], p[1]
        resources.append((int(x), int(y)))

    raw_obstacles = observation.get("obstacles") or []
    obstacles = set()
    for p in raw_obstacles:
        try:
            x, y = p
        except Exception:
            x, y = p[0], p[1]
        obstacles.add((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_key = None

    if not resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        best_metric = None
        for rx, ry in resources:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            metric = od - sd
            key = (metric, -sd, -abs(rx - ox) - abs(ry - oy), rx, ry)
            if best_metric is None or key > best_metric:
                best_metric = key

        if best_key is None or best_metric > best_key:
            best_key = best_metric
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
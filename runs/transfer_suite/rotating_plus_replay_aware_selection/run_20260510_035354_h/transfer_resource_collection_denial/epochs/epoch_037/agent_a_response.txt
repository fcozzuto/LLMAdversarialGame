def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res_set = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            res_set.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not res_set:
        return [0, 0]

    res_list = list(res_set)

    best_move = (0, 0)
    best_key = None  # maximize lexicographically

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        collected = 1 if (nx, ny) in res_set else 0

        # Choose best target resource from this hypothetical position
        best_target = None
        best_myd = 10**9
        best_priority = (-10**9, 10**9)
        for rx, ry in res_list:
            myd = cheb(nx, ny, rx, ry)
            opdist = cheb(ox, oy, rx, ry)
            # prefer closer resources; if tie, prefer ones we are closer to than opponent
            pri = (opdist - myd, -rx)  # deterministic bias
            if myd < best_myd or (myd == best_myd and pri > best_priority):
                best_myd = myd
                best_priority = pri
                best_target = (rx, ry)

        rx, ry = best_target
        opd = cheb(ox, oy, rx, ry)
        # Key: collect first; then minimize my distance; also prefer outpacing opponent
        key = (
            collected,
            -best_myd,
            (opd - best_myd),
            -cheb(nx, ny, w - 1, h - 1),  # slight deterministic drift
            -dx, -dy
        )

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
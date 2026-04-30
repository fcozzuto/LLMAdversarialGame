def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = [(x, y) for x, y in resources if (x, y) not in obstacles]
    if not res:
        return [0, 0]

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = (0, 0)
    best_key = None

    # Strategic change: evaluate each neighbor by the best "advantage" over all resources.
    # Also incorporate opponent pressure by rewarding moves that keep a large lead margin.
    for dx, dy, nx, ny in legal:
        my_best = -10**9
        my_closest = 10**9
        op_closest = 10**9
        lead_min_margin = 10**9  # how hard it is for opponent to beat us on the closest resource

        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if opd - myd > my_best:
                my_best = opd - myd
            if myd < my_closest:
                my_closest = myd
            if opd < op_closest:
                op_closest = opd

        # Lead margin: prefer states where my closest resource is not easily reachable by opponent.
        # Compute based on the resource that minimizes myd - opd (most opponent-ahead).
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            margin = (opd - myd)
            if margin < lead_min_margin:
                lead_min_margin = margin

        # Key: maximize advantage, then maximize worst-case margin, then minimize my distance to closest resource,
        # then minimize opponent distance, then deterministic geometric tie-break.
        k = (my_best, lead_min_margin, -my_closest, -op_closest, dx, dy)
        if best_key is None or k > best_key:
            best_key = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_key = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue

        opp_closer_count = 0
        max_adv = -10**9
        my_best = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if opd < myd:
                opp_closer_count += 1
            adv = opd - myd
            if adv > max_adv:
                max_adv = adv
            if myd < my_best:
                my_best = myd

        # Prefer: larger max advantage vs opponent, then fewer resources where opponent is closer,
        # then smaller distance to closest resource.
        key = (max_adv, -opp_closer_count, -my_best)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]
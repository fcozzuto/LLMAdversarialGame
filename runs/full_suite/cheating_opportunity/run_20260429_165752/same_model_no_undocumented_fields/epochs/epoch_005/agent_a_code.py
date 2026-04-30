def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set(map(tuple, obstacles))
    res_list = [tuple(r) for r in resources]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if (x, y) in obs_set:
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break: stable iteration order.
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        if not res_list:
            score = 0
        else:
            myd = 10**9
            od_to_myd = 0
            for rx, ry in res_list:
                d1 = cheb(nx, ny, rx, ry)
                if d1 < myd:
                    myd = d1
                    od_to_myd = cheb(ox, oy, rx, ry)
                elif d1 == myd:
                    d2 = cheb(ox, oy, rx, ry)
                    if d2 < od_to_myd:
                        od_to_myd = d2
            # Prefer grabbing soon and positions where we are not behind opponent.
            score = (100 - myd * 5) + (15 if myd <= od_to_myd else 0) - (od_to_myd if myd > od_to_myd else 0)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
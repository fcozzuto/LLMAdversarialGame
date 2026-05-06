def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # head toward opponent to disrupt
        bestd = 10**9
        best = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # choose move that maximizes our advantage for the best contestable resource,
        # and secondarily reduces distance to opponent (denial/intercept).
        move_best = -10**18
        for rx, ry in resources:
            ds_next = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # primary: advantage over opponent if both go for r
            adv = do - ds_next
            # secondary: prefer moves closer to opponent to contest space
            block = -cheb(nx, ny, ox, oy) // 4
            # tertiary: prefer higher resource coordinates tie-break deterministically
            tieb = -(rx + ry)
            val = adv * 100 + block + tieb
            if val > move_best:
                move_best = val
        if move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= W or ny < 0 or ny >= H:
                continue
            if (nx, ny) in obstacles:
                continue
            my_best_adv = -10**9
            my_best_mind = 10**9
            for rx, ry in resources:
                dmy = cheb(nx, ny, rx, ry)
                dop = cheb(ox, oy, rx, ry)
                adv = dop - dmy  # positive means we are closer than opponent to that resource
                if adv > my_best_adv or (adv == my_best_adv and dmy < my_best_mind):
                    my_best_adv = adv
                    my_best_mind = dmy
            # Encourage improvement when contested; lightly avoid standing adjacent to opponent.
            val = my_best_adv * 12 - my_best_mind - 0.05 * cheb(nx, ny, ox, oy)
            key = (-val, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]
    else:
        tx, ty = W // 2, H // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= W or ny < 0 or ny >= H:
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]
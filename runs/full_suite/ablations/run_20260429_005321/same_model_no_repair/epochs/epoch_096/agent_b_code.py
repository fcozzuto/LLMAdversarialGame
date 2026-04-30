def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    adj = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def obst_pen(x, y):
        p = 0
        for dx, dy in adj:
            if (x + dx, y + dy) in obst:
                p += 1
        return p

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If already on a resource, do nothing.
    for rx, ry in resources:
        if sx == rx and sy == ry:
            return [0, 0]

    best_move = None
    best_val = -10**18

    # Prefer moves that create the largest distance advantage vs opponent on some resource.
    for dx, dy, nx, ny in legal:
        if resources:
            best_adv = -10**18
            best_self_dist = 10**9
            best_opp_dist = 10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                adv = do - ds
                if adv > best_adv or (adv == best_adv and ds < best_self_dist) or (adv == best_adv and ds == best_self_dist and do < best_opp_dist):
                    best_adv, best_self_dist, best_opp_dist = adv, ds, do
            # If no positive advantage, fall back to minimizing self distance.
            if best_adv < 0:
                val = -best_self_dist - 0.3 * obst_pen(nx, ny)
            else:
                val = 1000 * best_adv - 0.5 * best_self_dist - 0.3 * obst_pen(nx, ny)
        else:
            val = -cheb(nx, ny, w // 2, h // 2) - 0.3 * obst_pen(nx, ny)

        # Small tie-breaker: move slightly toward top-left deterministically.
        val -= 0.001 * (nx + 2 * ny)

        if best_move is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
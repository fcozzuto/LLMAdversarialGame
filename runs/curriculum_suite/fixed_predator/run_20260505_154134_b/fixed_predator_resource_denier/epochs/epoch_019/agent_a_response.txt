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

    def greedy_opp_step(tx, ty):
        # opponent picks the move that minimizes Cheb distance to (tx,ty)
        best = (10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    nx, ny = ox, oy
                else:
                    nx, ny = ox + dx, oy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = cheb(nx, ny, tx, ty)
                if d < best[0]:
                    best = (d, dx, dy)
        return best[1], best[2]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # choose the most "deniable" resource after this move
        chosen = None
        chosen_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = (do - ds)  # positive means we are closer than opponent
            if val > chosen_val:
                chosen_val = val
                chosen = (rx, ry)

        if chosen is None:
            continue

        tx, ty = chosen
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        score = (do - ds)

        # slight preference for nearer pickups among same denial value
        score += -0.05 * ds
        score += -0.001 * (tx + ty)

        # if opponent can reach chosen resource next move (Cheb distance 1) while we can't,
        # penalize to avoid getting out-tempo'd
        opp_dx, opp_dy = greedy_opp_step(tx, ty)
        onx, ony = ox + opp_dx, oy + opp_dy
        if inb(onx, ony) and (onx, ony) not in obstacles:
            if cheb(onx, ony, tx, ty) <= 1 and ds > 1:
                score -= 5.0

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
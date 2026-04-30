def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in occ:
            continue

        # Obstacle vicinity penalty (encourage safer corridors)
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in occ:
                    adj_pen += 3 if ax == 0 or ay == 0 else 2

        # Compute best immediate advantage after this move (opponent position fixed)
        # Higher is better.
        best_adv = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Advantage: we want do - ds large; tie-break toward closer ds
            adv = (do - ds) * 100 - ds
            if adv > best_adv:
                best_adv = adv

        # Also discourage moves that give the opponent a closer contested target by moving away
        # from our current best target direction roughly via ds decrease.
        cur_best = 10**18
        for rx, ry in resources:
            cur_best = min(cur_best, cheb(sx, sy, rx, ry))
        new_best = 10**18
        for rx, ry in resources:
            new_best = min(new_best, cheb(nx, ny, rx, ry))
        retreat_pen = 0
        if new_best > cur_best:
            retreat_pen = (new_best - cur_best) * 30

        score = best_adv - adj_pen - retreat_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
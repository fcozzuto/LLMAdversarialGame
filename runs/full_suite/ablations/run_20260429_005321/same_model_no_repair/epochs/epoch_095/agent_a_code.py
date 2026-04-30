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

    def obst_penalty(x, y):
        p = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in obst:
                p += 2
        return p

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Prefer resources where we are closer than opponent; if no advantage, minimize our distance.
    best = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        if resources:
            local = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Primary: make advantage bigger. Secondary: close in even if behind.
                val = (do - ds) * 10 - ds - obst_penalty(nx, ny)
                if val > local:
                    local = val
            score = local
        else:
            score = -cheb(nx, ny, ox, oy) - obst_penalty(nx, ny)

        # Mildly avoid moving onto lines that could let opponent immediately take a resource:
        # if we move farther from the best current target (by our perspective), discourage.
        if resources:
            cur_best = -10**18
            for rx, ry in resources:
                ds0 = cheb(sx, sy, rx, ry)
                do0 = cheb(ox, oy, rx, ry)
                val0 = (do0 - ds0) * 10 - ds0
                if val0 > cur_best:
                    cur_best = val0
            if score < cur_best:
                score -= 1

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
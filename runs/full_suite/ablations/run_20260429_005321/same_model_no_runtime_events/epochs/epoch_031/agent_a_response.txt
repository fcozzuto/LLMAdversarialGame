def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best = None
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        if resources:
            # Race score: sum over resources where we can beat opponent, plus chase for closest.
            val = 0.0
            my_best = 10**9
            opp_best = 10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                if myd < my_best: my_best = myd
                if opd < opp_best: opp_best = opd
                d = opd - myd  # positive if we are closer after this move
                if d > 0:
                    # Encourage winning a specific nearby resource, stronger when close.
                    val += 3.0 * d - 0.2 * myd
                else:
                    # Slightly penalize moving where we fall behind.
                    val += 0.15 * d
            # If we can't beat anyone now, still minimize our distance to nearest resource.
            val += 1.5 * (opp_best - my_best)
        else:
            val = 0.0

        # Center preference to avoid dithering; also lightly avoid adjacency to opponent.
        dist_center = cheb(nx, ny, int(round(cx)), int(round(cy)))
        val -= 0.02 * dist_center
        opp_adj = cheb(nx, ny, ox, oy)
        val -= 0.03 * (1 if opp_adj == 0 else 0)  # discourage staying on opponent (if possible)

        # Tie-break deterministically by move order encoded in dx,dy.
        key = (val, -abs(dx) - abs(dy), -dx, -dy)
        if best is None or key > best:
            best = key
            best_val = val
            best_move = [dx, dy]

    return best_move
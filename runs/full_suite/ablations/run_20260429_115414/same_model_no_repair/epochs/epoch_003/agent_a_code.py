def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            # Avoid opponent and obstacles (local)
            v = cheb(nx, ny, cx, cy)
            v += 0.3 * cheb(nx, ny, ox, oy)
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if (nx + ax, ny + ay) in obs:
                        v += 0.8
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # For each move, choose resource giving max advantage (opponent farther than us).
    best = None
    bestv = None
    for dx, dy, nx, ny in moves:
        # obstacle adjacency penalty
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obs:
                    p += 1
        # advantage: want our distance smaller than opponent's for the same resource
        best_adv = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # also slightly prefer closer resources overall once advantage is similar
            adv = (do - ds) - 0.02 * ds
            if best_adv is None or adv > best_adv:
                best_adv = adv
        # discourage moving next to opponent when advantage ties
        tie_break = 0.05 * cheb(nx, ny, ox, oy)
        v = -best_adv + p * 0.6 + tie_break
        if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]
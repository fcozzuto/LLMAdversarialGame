def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) in res:
            return [dx, dy]

        if not res:
            # If no resources visible, improve relative distance to opponent (avoid giving chase).
            v = cheb(ox, oy, nx, ny) - cheb(ox, oy, sx, sy)
            if v > best_val:
                best_val = v
                best_move = (dx, dy)
            continue

        # Choose the target where we can arrive first by the largest margin; tie-break by earliest arrival.
        best_t = -10**18
        for tx, ty in res:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            margin = opd - myd
            arrival = myd
            val = margin * 100 - arrival
            if val > best_t:
                best_t = val
        # Small secondary: prefer moves that move toward the best target region (deterministic via value only).
        if best_t > best_val:
            best_val = best_t
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
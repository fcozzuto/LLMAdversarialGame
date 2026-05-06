def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

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
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18

    # Heuristic: pick move that maximizes the best advantage margin over remaining resources,
    # with small preference for getting closer to that chosen resource and away from obstacles.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        wall_pen = 0
        for ax, ay in dirs:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in obs:
                wall_pen += 1

        best_cell_margin = -10**18
        best_cell_dist = 10**9
        for cx, cy in resources:
            sd = cheb(nx, ny, cx, cy)
            od = cheb(ox, oy, cx, cy)
            margin = od - sd  # positive means we can reach earlier (or at least closer in cheb time)
            # Slight tie-break: prefer smaller self distance among similar margins.
            if margin > best_cell_margin or (margin == best_cell_margin and sd < best_cell_dist):
                best_cell_margin = margin
                best_cell_dist = sd

        # Encourage attacking: high margin dominates; then closer distance; then slight wall avoidance.
        val = best_cell_margin * 1000 - best_cell_dist - wall_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    if resources:
        res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    else:
        res = []

    for dx, dy, nx, ny in legal:
        if not res:
            # Drift toward center while keeping away from opponent.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            v = -cheb(nx, ny, ox, oy) + 0.35 * cheb(nx, ny, cx, cy) - 0.01 * (nx + ny)
        else:
            # Choose move that improves access to resources while denying opponent.
            v = -10**18
            for rx, ry in res:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer closer-to-resource, and prefer resources farther from opponent.
                # Add slight tie-break toward moving along diagonals for faster convergence.
                w_diag = 1 if (nx != sx and ny != sy) else 0
                cand = (-ds) + 0.85 * do + 0.02 * w_diag
                if cand > v:
                    v = cand

            # Obstacle/edge pressure: avoid getting stuck against boundaries.
            edge_pen = 0
            if nx == 0 or nx == w - 1: edge_pen += 1
            if ny == 0 or ny == h - 1: edge_pen += 1
            v -= 0.25 * edge_pen

            # If we can reach a resource immediately, strongly prefer that.
            for rx, ry in res:
                if cheb(nx, ny, rx, ry) == 0:
                    v += 10**6
                    break

        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
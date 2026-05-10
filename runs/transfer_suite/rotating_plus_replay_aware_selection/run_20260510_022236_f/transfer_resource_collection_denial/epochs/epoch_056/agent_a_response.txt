def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obstacle_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                    pen += 1
        return pen

    # Choose a move that maximizes our best resource value after moving one step.
    # Resource value prefers being closer than opponent; otherwise still prefers progress.
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        pen = adj_obstacle_pen(nx, ny)

        local_best = -10**18
        for rx, ry in res:
            sd = cheb_dist(nx, ny, rx, ry)
            od = cheb_dist(ox, oy, rx, ry)
            lead = od - sd  # positive means we are closer/equal
            # Big weight on having lead; secondary on decreasing our distance.
            val = 40 * lead - sd - 2 * pen
            # Small deterministic tie-breaker: favor resources with lower lex order.
            val -= (rx * 0.0001 + ry * 0.000001)
            if val > local_best:
                local_best = val

        # Prefer moves that actually improve our distance to the current best resource estimate.
        # Deterministic tie-break: prefer staying in bounds center-ish (lower manhattan to center).
        center_bonus = -(abs((nx - (w - 1) / 2)) + abs((ny - (h - 1) / 2))) * 0.00001
        total = local_best + center_bonus

        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
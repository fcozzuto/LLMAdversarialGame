def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_obs_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                    pen += 1
        return pen

    # Choose move that maximizes expected advantage for closest "contested" resource
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        base = -0.05 * (dx * dx + dy * dy)
        pen = 0.2 * adj_obs_pen(nx, ny)

        # Evaluate against the best resource we can potentially reach first
        val = -10**18
        self_d0 = cheb(nx, ny, ox, oy)  # small stabilizer: avoid drifting into opponent
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If we can be closer soon, prioritize; otherwise still move toward far valuable resources
            advantage = (od - sd)
            tie_bonus = 0.15 if sd == od else 0.0
            # Slight preference for nearer resources to reduce overshooting
            local = 1.25 * advantage + tie_bonus - 0.03 * sd - 0.01 * (cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry))
            if local > val:
                val = local

        # Global preference: also head toward the single nearest resource when advantage is small
        if val < 0.2:
            # nearest resource by our distance
            sdmin = 10**9
            nearest = None
            for rx, ry in res:
                sd = cheb(nx, ny, rx, ry)
                if sd < sdmin:
                    sdmin = sd
                    nearest = (rx, ry)
            if nearest is not None:
                rx, ry = nearest
                val = 0.6 * (cheb(sx, sy, rx, ry) - cheb(nx, ny, rx, ry)) - 0.02 * sdmin

        total = base + val - pen - 0.003 * self_d0
        if total > best_val + 1e-12 or (abs(total - best_val) <= 1e-12 and (dx, dy) == (0, 0)):
            best_val = total
            best_move = [dx, dy]

    return best_move
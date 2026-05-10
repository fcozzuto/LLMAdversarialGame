def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacle_set

    def adj_obs_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacle_set:
                    pen += 1
        return pen

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        self_pen = adj_obs_pen(nx, ny)

        # Greedy but with denial awareness: prefer resources where we are closer than opponent.
        best_res = -10**18
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                # Immediate pickup
                best_res = 10**9
                break
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            rel = do - ds  # positive means we're closer
            # Weight: get closer quickly, and deny opponent.
            val = rel * 50 - ds * 3 - do * 0.5
            if val > best_res:
                best_res = val

        # Minor center preference to reduce being trapped by obstacles
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center_bias = -0.01 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        total = best_res - self_pen * 25 + center_bias
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
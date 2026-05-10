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
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        self_pen = adj_obs_pen(nx, ny)
        best_res_val = -10**18
        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; break ties by proximity.
            # Slightly penalize moves that run near obstacles.
            v = (opp_d - self_d) * 10 - self_d - self_pen * 0.7
            if v > best_res_val:
                best_res_val = v

        # Tie-break deterministically: prefer smaller self_d to any resource, then stable move order.
        if best_res_val > best_val:
            best_val = best_res_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
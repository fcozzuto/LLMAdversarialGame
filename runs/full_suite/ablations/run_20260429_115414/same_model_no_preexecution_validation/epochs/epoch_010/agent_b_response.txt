def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs_set

    def obs_pen(x, y):
        if not obstacles:
            return 0
        best = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
                if best == 0:
                    return 10**7
                if best == 1:
                    break
        if best == 1:
            return 20
        if best == 2:
            return 8
        if best == 3:
            return 3
        return 0

    def opp_resource_pressure(rx, ry):
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        # Prefer resources we're closer to; otherwise slightly penalize.
        return -4 if my_d <= op_d else 4

    def best_target_dist(x, y):
        if not resources:
            # fall back to center
            cx, cy = w // 2, h // 2
            return cheb(x, y, cx, cy)
        best = 10**9
        for rx, ry in resources:
            my_d = cheb(x, y, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Ensure we don't chase resources opponent is likely taking.
            score = my_d + (2 if op_d < my_d else 0) + (0 if my_d <= op_d else 1)
            if score < best:
                best = score
        return best

    best_move = (0, 0)
    best_val = None
    # Evaluate moves with lookahead: minimize distance-to-best-target + obstacle penalty + small opponent pressure.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        base = best_target_dist(nx, ny)
        val = base + obs_pen(nx, ny)
        # When choosing between targets, also incorporate whether we'd lose it to opponent.
        if resources:
            # tie-break: favor moves that reduce (my_d - op_d) towards negative.
            tmin = 10**9
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                op_d = cheb(ox, oy, rx, ry)
                score = my_d - op_d
                if score < tmin:
                    tmin = score
            val += 0.5 * tmin
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
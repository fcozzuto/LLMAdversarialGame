def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_val = -10**18

    # If we can clearly beat the opponent on a resource, prioritize it.
    # Otherwise, go to a resource while maximizing separation from the opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        if resources:
            my_best = -10**18
            my_d_to_best = 10**9
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                advantage = d_op - d_me  # positive means we reach sooner/equal better
                # Strongly prefer winning access; otherwise still prefer smaller own distance.
                val = 6 * advantage - d_me
                if val > my_best or (val == my_best and d_me < my_d_to_best):
                    my_best = val
                    my_d_to_best = d_me
            # Add anti-chase pressure: keep distance from opponent unless we are winning.
            sep = cheb(nx, ny, ox, oy)
            op_push = -0.6 * (sep if my_best > 0 else -sep)  # if winning, less penalty for closeness; else avoid closeness
            # Deterministic tie-break toward staying nearer to center.
            cx, cy = w // 2, h // 2
            center_bias = -0.05 * cheb(nx, ny, cx, cy)
            val = my_best + op_push + center_bias
        else:
            # No visible resources: move away from opponent toward center.
            sep = cheb(nx, ny, ox, oy)
            cx, cy = w // 2, h // 2
            val = 1.5 * sep - 0.1 * cheb(nx, ny, cx, cy)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
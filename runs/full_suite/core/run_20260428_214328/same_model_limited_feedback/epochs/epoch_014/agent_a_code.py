def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cd(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    if (sx, sy) in obstacles:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    best_move = (0, 0)
    best_val = None
    center = (w // 2, h // 2)
    alpha = 0.9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            my_best = None
            for rx, ry in resources:
                d_s = cheb((nx, ny), (rx, ry))
                d_o = cheb((ox, oy), (rx, ry))
                val = d_s - alpha * d_o
                val += 0.01 * cd((nx, ny), (rx, ry))
                if my_best is None or val < my_best:
                    my_best = val
            val = my_best
        else:
            val = cheb((nx, ny), center)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
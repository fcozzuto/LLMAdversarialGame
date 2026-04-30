def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    w, h = observation["grid_width"], observation["grid_height"]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            move_best = -10**9
            for rx, ry in resources:
                ds = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                val = (do - ds) * 10 - ds
                if val > move_best:
                    move_best = val
            val = move_best
        else:
            val = -dist(nx, ny, ox, oy)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is not None:
        return [int(best[0]), int(best[1])]
    return [0, 0]
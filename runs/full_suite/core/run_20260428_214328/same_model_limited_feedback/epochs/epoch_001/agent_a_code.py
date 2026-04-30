def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_for_target(tx, ty):
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = (nx - tx) ** 2 + (ny - ty) ** 2
            key = (d, abs(nx - ox) ** 2 + abs(ny - oy) ** 2, nx, ny, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        if best is None:
            return [0, 0]
        return best[1]

    if resources:
        # Choose the target resource that we can reach most directly, then move toward it.
        best_key = None
        best_target = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            key = ((sx - rx) ** 2 + (sy - ry) ** 2, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_target = (rx, ry)
        tx, ty = best_target
        return best_for_target(tx, ty)

    # No visible resources: move to gain future advantage by heading toward opponent's corner.
    # Assume corners are (0,0) and (w-1,h-1); opponent starts opposite, so infer likely target corner.
    my_goal = (0, 0) if (ox, oy) == (w - 1, h - 1) else (w - 1, h - 1)
    return best_for_target(my_goal[0], my_goal[1])
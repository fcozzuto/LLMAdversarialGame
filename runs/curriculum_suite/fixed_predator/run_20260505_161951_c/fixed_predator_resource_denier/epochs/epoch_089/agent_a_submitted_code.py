def choose_move(observation):
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", None) or []
    obstacles = observation.get("obstacles", None) or []
    obs = set(obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def score_move(nx, ny):
        if resources:
            best = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < best:
                    best = d
            return -best
        return (abs(nx - ox) + abs(ny - oy))

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue
        v = score_move(nx, ny)
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best if best is not None else [0, 0]
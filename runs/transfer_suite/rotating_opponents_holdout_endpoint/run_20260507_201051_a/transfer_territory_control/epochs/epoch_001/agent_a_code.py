def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obstacles_list)
    resources_list = observation.get("resources", []) or []
    resources = set(tuple(p) for p in resources_list)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    bestv = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_res = None
        if resources:
            d_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        v = -d_opp * 10
        if d_res is not None:
            v += max(0, 50 - d_res)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dpo = abs(nx - ox) + abs(ny - oy)
            key = (-dpo, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        return best if best is not None else [0, 0]

    def nearest_dist(x, y):
        md = None
        for rx, ry in resources:
            d = abs(x - rx) + abs(y - ry)
            if md is None or d < md:
                md = d
        return md if md is not None else 10**9

    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dres = nearest_dist(nx, ny)
        dpo = abs(nx - ox) + abs(ny - oy)
        # primary: get closer to nearest resource; secondary: keep farther from opponent
        key = (dres, -dpo, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res_cells.append((x, y))

    if not res_cells:
        # No reachable resources: move to best contest position vs opponent (min distance)
        target = (ox, oy)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                d = abs(nx - target[0]) + abs(ny - target[1])
                cand = (d, dx, dy)
                if best is None or cand < best:
                    best = cand
        return [best[1], best[2]] if best is not None else [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    nearest = min(res_cells, key=lambda p: (man((sx, sy), p), p[0], p[1]))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            d = abs(nx - nearest[0]) + abs(ny - nearest[1])
            cand = (d, abs(dx), abs(dy), dx, dy)
            if best is None or cand < best:
                best = cand

    return [best[3], best[4]] if best is not None else [0, 0]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    opts = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    if resources:
        best = None
        for dx, dy in opts:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            best_diff = None
            best_my = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                diff = myd - opd
                if best_diff is None or diff < best_diff or (diff == best_diff and (best_my is None or myd < best_my)):
                    best_diff = diff
                    best_my = myd
            key = (best_diff, best_my, nx, ny)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return best[1] if best is not None else [0, 0]

    # No resources: drift toward center while avoiding obstacles
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, cx, cy)
        key = (d, nx, ny)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return best[1] if best is not None else [0, 0]
def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", None) or []
    obstacles_list = observation.get("obstacles", None) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not moves:
        return [0, 0]
    best_move = (0, 0)
    best_score = -10**18
    if resources:
        best_r = None
        for p in resources:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if ok(x, y):
                    d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
                    if best_r is None or d < best_r[0]:
                        best_r = (d, x, y)
        if best_r is None:
            resources = []
        else:
            rx, ry = best_r[1], best_r[2]
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not ok(nx, ny):
                    continue
                dR = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                dO = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
                score = -dR * 10 + dO
                if score > best_score:
                    best_score = score
                    best_move = (dx, dy)
            return [best_move[0], best_move[1]]
    # No resources or none reachable: move toward center while avoiding opponent
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dC = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        dO = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = -dC * 3 + dO
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]
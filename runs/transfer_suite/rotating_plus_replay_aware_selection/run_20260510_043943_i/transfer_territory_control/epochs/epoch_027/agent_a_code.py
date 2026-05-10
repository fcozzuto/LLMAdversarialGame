def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def score(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h):
            return -10**9
        if (nx, ny) in obstacles:
            return -10**9
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        if d_to_opp == 0:
            return -10**8
        best_res = 10**9
        for rx, ry in resources:
            d = abs(nx - rx) + abs(ny - ry)
            if d < best_res:
                best_res = d
        if resources:
            return (10000 - best_res * 10) + d_to_opp
        return -((nx - cx) ** 2 + (ny - cy) ** 2) + d_to_opp

    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        s = score(nx, ny)
        if s > best[0]:
            best = (s, dx, dy)
    return [best[1], best[2]]
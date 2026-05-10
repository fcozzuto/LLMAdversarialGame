def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for c in (observation.get("obstacles", []) or []):
        if c is None:
            continue
        obstacles.add((int(c[0]), int(c[1])))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = observation.get("resources", None)
    target = (ox, oy)
    if res:
        best = None
        bestd = None
        for r in res:
            if r is None or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) or (rx, ry) in obstacles:
                continue
            d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
            if bestd is None or d < bestd:
                bestd = d
                best = (rx, ry)
        if best is not None:
            target = best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_to_t = (nx - target[0]) * (nx - target[0]) + (ny - target[1]) * 0 + (ny - target[1]) * (ny - target[1])
        dist_to_center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        dist_to_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val = -dist_to_t + 0.05 * (-dist_to_center) + 0.02 * dist_to_opp
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move
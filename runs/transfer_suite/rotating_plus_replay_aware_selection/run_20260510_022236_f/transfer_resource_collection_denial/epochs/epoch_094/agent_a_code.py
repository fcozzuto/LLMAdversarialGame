def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid_res.append((x, y))
    if not valid_res:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_resource_score(px, py):
        best = None
        for rx, ry in valid_res:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive => we are closer than opponent
            y_pref = -abs(ry - (h - 1) / 2.0)
            cand = (lead, -ds, y_pref, -abs(rx - (w - 1) / 2.0))
            if best is None or cand > best:
                best = cand
        return best

    best_move = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = best_resource_score(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
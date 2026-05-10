def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obs:
            moves.append((nx, ny))
    if not moves:
        return [0, 0]

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = r
            rx, ry = int(x), int(y)
            if in_bounds(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))
        except:
            continue

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if res:
        best = None
        for rx, ry in res:
            ds = manh(sx, sy, rx, ry)
            do = manh(ox, oy, rx, ry)
            margin = ds - do
            score = (margin, ds, rx, ry)
            if best is None or score < best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
        best_move = None
        best_val = None
        for nx, ny in moves:
            d = manh(nx, ny, tx, ty)
            opp_d = manh(nx, ny, ox, oy)
            val = (d, -opp_d, nx, ny)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (nx, ny)
        return [best_move[0] - sx, best_move[1] - sy]

    best_move = None
    best_d = None
    for nx, ny in moves:
        d = manh(nx, ny, ox, oy)
        val = (-d, nx, ny)
        if best_d is None or val < best_d:
            best_d = val
            best_move = (nx, ny)
    return [best_move[0] - sx, best_move[1] - sy]
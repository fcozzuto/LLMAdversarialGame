def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    if w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if p is None:
            continue
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells") or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if unclaimed:
        best_t = None
        best_key = None
        for p in unclaimed:
            if p is None:
                continue
            try:
                tx, ty = p
                tx, ty = int(tx), int(ty)
            except:
                continue
            if not inside(tx, ty) or (tx, ty) in obstacles:
                continue
            d1 = man(sx, sy, tx, ty)
            d2 = man(ox, oy, tx, ty)
            k = (d1 - 0.7 * d2, abs(tx - cx) + abs(ty - cy), tx, ty)
            if best_key is None or k < best_key:
                best_key = k
                best_t = (tx, ty)
        target = best_t if best_t is not None else (ox, oy)
    else:
        target = (ox, oy)

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dt = man(nx, ny, target[0], target[1])
        do = man(nx, ny, ox, oy)
        center = abs(nx - cx) + abs(ny - cy)
        score = dt - 0.55 * do + 0.02 * center
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move
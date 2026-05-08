def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p[0], p[1]
            x, y = int(x), int(y)
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        try:
            x, y = r[0], r[1]
            x, y = int(x), int(y)
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not res:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = None
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = md(nx, ny, tx, ty)
            if best is None or d < best_d or (d == best_d and (dx, dy) < best):
                best, best_d = (dx, dy), d
        return [best[0], best[1]]

    best = None
    best_val = None
    best_d2 = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        dmin = None
        for rx, ry in res:
            d = md(nx, ny, rx, ry)
            if dmin is None or d < dmin:
                dmin = d
        d_op = md(nx, ny, ox, oy)
        val = (dmin, -d_op)  # primary: closer to a resource; secondary: farther from opponent
        if best is None or val < best_val or (val == best_val and (dx, dy) < best):
            best, best_val, best_d2 = (dx, dy), val, d_op
    return [best[0], best[1]]
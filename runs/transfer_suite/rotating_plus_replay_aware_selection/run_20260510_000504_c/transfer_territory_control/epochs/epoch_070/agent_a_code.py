def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for o in (observation.get("obstacles") or []):
        try:
            obstacles.add((o[0], o[1]))
        except Exception:
            pass

    resources = observation.get("resources") or []
    opp = observation.get("opponent_position") or None
    ox = oy = None
    if opp is not None:
        ox, oy = opp[0], opp[1]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    cx, cy = (w - 1) // 2, (h - 1) // 2
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1), (0, 0)]

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            # nearest resource
            dmin = None
            for r in resources:
                tx, ty = r[0], r[1]
                d = dist(nx, ny, tx, ty)
                if dmin is None or d < dmin:
                    dmin = d
            v = -dmin
        else:
            # avoid opponent, otherwise head to center
            if ox is not None:
                v = dist(nx, ny, ox, oy)
            else:
                v = -dist(nx, ny, cx, cy)
        if best is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
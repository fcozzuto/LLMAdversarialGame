def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w)
        h = int(h)
    except:
        w = 8
        h = 8

    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    sx, sy = to_xy(observation.get("self_position"))
    ox, oy = to_xy(observation.get("opponent_position"))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_t = resources[0]
        best_key = None
        for (rx, ry) in resources:
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            key = (opd - myd, -myd, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_t = (rx, ry)
        rx, ry = best_t
        best_move = (0, 0)
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            score = (opd - myd, -myd)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: keep away from opponent, prefer staying valid and in-bounds.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, ox, oy)
        score = (myd, -abs(nx - sx) - abs(ny - sy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best
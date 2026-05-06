def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs_list = observation.get("obstacles") or []
    obstacles = set(map(tuple, obs_list))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((r[0], r[1]))

    if not res:
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = man(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = -10**9
        for rx, ry in res:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            val = (d_op - d_me) - 0.01 * d_me
            if val > score:
                score = val
        if bestv is None or score > bestv:
            bestv, best = score, (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                best = (dx, dy)
                break
    return [best[0], best[1]] if best is not None else [0, 0]
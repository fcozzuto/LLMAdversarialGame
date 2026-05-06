def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = observation.get("grid_width", 0), observation.get("grid_height", 0)
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((r[0], r[1]))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b
    legal = [(dx, dy) for dx, dy in moves if inside(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]
    best = None
    bestv = -10**18
    target_cx, target_cy = w // 2, h // 2
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if res:
            ds = min(md(nx, ny, rx, ry) for rx, ry in res)
            do = min(md(ox, oy, rx, ry) for rx, ry in res)
            v = -ds + 0.35 * do + 0.02 * (md(nx, ny, target_cx, target_cy) * -1)
        else:
            v = -md(nx, ny, target_cx, target_cy) + 0.25 * md(nx, ny, ox, oy) * -1
        if best is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]
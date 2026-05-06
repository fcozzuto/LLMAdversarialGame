def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = observation.get("obstacles") or []
    blocked = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if (x, y) not in blocked:
                res.append((x, y))

    if not res:
        dx = 0
        dy = 0
        best = None
        dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
        for tx, ty in [(sx + dx, sy + dy) for dx, dy in dirs]:
            x, y = tx, ty
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                key = (abs(ox - x) + abs(oy - y), x, y)
                if best is None or key < best[0]:
                    best = (key, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def edge_pen(x, y):
        m = min(x, y, w - 1 - x, h - 1 - y)
        if m <= 0:
            return 120
        if m == 1:
            return 60
        if m == 2:
            return 25
        return 0

    best = None
    for rx, ry in res:
        d_self = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        can_take = d_self - d_opp
        key = (can_take, d_self + edge_pen(rx, ry), rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    candidates = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    best_step = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        score = (man(nx, ny, tx, ty), edge_pen(nx, ny), man(nx, ny, ox, oy), nx, ny)
        if best_step is None or score < best_step[0]:
            best_step = (score, dx, dy)

    if best_step is None:
        return [0, 0]
    return [best_step[1], best_step[2]]
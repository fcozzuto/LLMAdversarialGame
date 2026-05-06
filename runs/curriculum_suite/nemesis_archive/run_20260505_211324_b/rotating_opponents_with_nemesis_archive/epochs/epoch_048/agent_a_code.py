def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    for tx, ty in res:
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        key = (ds - do, ds, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    _, (tx, ty) = best

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    order = []
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    if dx != 0:
        order.append((dx, 0))
    if dy != 0:
        order.append((0, dy))
    for m in moves:
        if m not in order:
            order.append(m)

    for mx, my in order:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [mx, my]
    return [0, 0]
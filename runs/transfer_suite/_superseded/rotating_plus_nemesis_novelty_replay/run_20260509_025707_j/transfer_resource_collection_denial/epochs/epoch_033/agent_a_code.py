def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list if p is not None and len(p) >= 2}
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def resource_key(r):
        rx, ry = r[0], r[1]
        if not ok(rx, ry):
            return (-10**9, 10**9)
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer resources we can reach earlier (bigger od-sd), then shorter our distance
        return (od - sd, -sd)

    target = None
    bestk = None
    for r in resources:
        if r is None or len(r) < 2:
            continue
        k = resource_key(r)
        if bestk is None or k > bestk or (k == bestk and (r[0], r[1]) < target):
            bestk = k
            target = (r[0], r[1])

    if target is None:
        return [0, 0]

    tx, ty = target
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        self_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, nx, ny)
        # Also prefer moves that reduce directionally toward target (tie-break)
        dir_align = -abs((tx - nx) - (tx - sx)) - abs((ty - ny) - (ty - sy))
        cand = (self_d, opp_d, -dir_align, dx, dy)
        if best is None or cand < best:
            best = cand
    return [best[3], best[4]]
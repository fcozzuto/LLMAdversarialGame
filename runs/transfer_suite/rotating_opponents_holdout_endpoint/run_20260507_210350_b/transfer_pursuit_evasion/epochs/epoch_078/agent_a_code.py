def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = observation.get("resources", None)
    resources = []
    if isinstance(res, list):
        for r in res:
            if r is not None and len(r) >= 2:
                resources.append((int(r[0]), int(r[1])))
    if observation.get("remaining_resource_count", None) == 0 and resources:
        resources = []

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    if resources:
        tx, ty = min(resources, key=lambda p: (cd(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_t = cd(nx, ny, tx, ty)
        d_o = cd(nx, ny, ox, oy)
        sc = -d_t + (0.1 * d_o)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
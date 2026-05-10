def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step(dx, dy):
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return nx, ny
        return sx, sy

    if res:
        best = None
        for tx, ty in res:
            d1 = dist(sx, sy, tx, ty)
            d2 = dist(ox, oy, tx, ty)
            sc = (d2 - d1, -tx, -ty)  # prefer where I'm closer than opponent
            if best is None or sc > best[0]:
                best = (sc, (tx, ty))
        tx, ty = best[1]
        target_dx = 0 if tx == sx else (1 if tx > sx else -1)
        target_dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = []
        for dx, dy in moves:
            nx, ny = step(dx, dy)
            candidates.append((dist(nx, ny, tx, ty), abs(dx - target_dx) + abs(dy - target_dy), dx, dy))
        candidates.sort()
        return [int(candidates[0][2]), int(candidates[0][3])]

    # No resources known: move to maximize distance from opponent
    candidates = []
    for dx, dy in moves:
        nx, ny = step(dx, dy)
        candidates.append((-dist(nx, ny, ox, oy), dx, dy))
    candidates.sort()
    return [int(candidates[0][1]), int(candidates[0][2])]
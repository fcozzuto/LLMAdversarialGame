def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles

    moves = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    valid = [(dx, dy) for dx, dy in moves if ok(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            score = - (abs(nx - ox) + abs(ny - oy))
            key = (score, dx, dy)
            best = key if best is None or key > best else best
        _, dx, dy = best
        return [dx, dy]

    tx = tx2 = ty = ty2 = None
    bestd = None
    for x, y in resources:
        d = abs(x - sx) + abs(y - sy)
        key = (-d, x, y)
        if bestd is None or key > bestd:
            bestd = key
            tx, ty = x, y

    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d = abs(tx - nx) + abs(ty - ny)
        # Prefer moving closer to nearest resource; break ties deterministically and slightly avoid opponent
        score = -d * 10 - (abs(nx - ox) + abs(ny - oy))
        key = (score, -dx, -dy)
        best = key if best is None or key > best else best
    _, ndx, ndy = best
    return [ndx, ndy]
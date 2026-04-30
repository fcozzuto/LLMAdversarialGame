def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if resources:
        tx, ty = min(resources, key=lambda r: d2(sx, sy, r[0], r[1]))
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            key = (-d2(nx, ny, tx, ty), d2(nx, ny, ox, oy))
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        key = (d2(nx, ny, ox, oy), -abs(dx) - abs(dy))
        if best is None or key > best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]] if best else [0, 0]
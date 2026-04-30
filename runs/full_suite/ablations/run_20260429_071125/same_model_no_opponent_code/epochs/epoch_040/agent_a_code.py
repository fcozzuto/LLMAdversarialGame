def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        best_key = None
        for tx, ty in resources:
            key = (man((sx, sy), (tx, ty)) - man((ox, oy), (tx, ty)),
                   man((sx, sy), (tx, ty)),
                   tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
    else:
        tx, ty = (w // 2, h // 2)

    best_move = (0, 0)
    best_d = None
    best_t = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = man((nx, ny), (tx, ty))
        # tie-break deterministically
        tkey = (d, dx, dy, nx, ny)
        if best_t is None or tkey < best_t:
            best_t = tkey
            best_move = (dx, dy)
            best_d = d

    return [int(best_move[0]), int(best_move[1])]
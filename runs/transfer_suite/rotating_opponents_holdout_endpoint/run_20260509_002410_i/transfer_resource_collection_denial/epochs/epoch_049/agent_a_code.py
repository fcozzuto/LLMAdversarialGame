def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            if len(p) >= 2:
                obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        key = (od - sd, -sd, -ry, -rx)
        if best is None or key > best:
            best = key
            target = (rx, ry)
    if target is None:
        return [0, 0]

    tx, ty = target
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx in (dx0, 0, -dx0):
        if dx not in (-1, 0, 1):
            continue
        for dy in (dy0, 0, -dy0):
            if dy not in (-1, 0, 1):
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    best_move = None
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d_to = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        key = (-d_to, d_opp - d_to, -ny, -nx)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
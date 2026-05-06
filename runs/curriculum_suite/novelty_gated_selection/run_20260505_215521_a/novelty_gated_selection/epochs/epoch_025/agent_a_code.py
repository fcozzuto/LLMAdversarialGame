def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obst

    cx, cy = w // 2, h // 2

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            key = (man(nx, ny, cx, cy), abs(dx) + abs(dy))
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        best_res = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
            else:
                continue
            dself = man(nx, ny, rx, ry)
            dob = man(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent (maximize margin).
            # Deterministic tie-break by absolute closeness.
            margin = dob - dself
            key_r = (-margin, dself, dself - dob)
            if best_res is None or key_r < best_res:
                best_res = key_r
        key = best_res if best_res is not None else (10**9, 10**9, 0)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1] if best else [0, 0]
def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except Exception:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                ax, ay = int(p[0]), int(p[1])
            except Exception:
                continue
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                rx, ry = int(p[0]), int(p[1])
            except Exception:
                continue
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def score(nx, ny):
        best = 10**9
        for rx, ry in resources:
            d = abs(rx - nx) + abs(ry - ny)
            if d < best:
                best = d
        if resources:
            return -best * 100 + (0 if best == 0 else 0)
        cx, cy = (w - 1) // 2, (h - 1) // 2
        d1 = abs(cx - nx) + abs(cy - ny)
        d2 = abs(nx - ox) + abs(ny - oy)
        return -d1 * 10 + d2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    dx, dy = best_move
    if not ok(sx + dx, sy + dy):
        for dx, dy in moves:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [dx, dy]
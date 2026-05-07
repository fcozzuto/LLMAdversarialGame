def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    targets = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                targets.append((x, y))

    if not targets:
        return [0, 0]

    base = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)
    if t & 1:
        base = base[4:] + base[:4]

    def d2(a, b, x, y):
        dx = a - x
        dy = b - y
        return dx * dx + dy * dy

    best = None
    best_move = [0, 0]
    for dx, dy in base:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        mind = 10**18
        for tx, ty in targets:
            v = d2(nx, ny, tx, ty)
            if v < mind:
                mind = v
        opp_close = d2(nx, ny, ox, oy)
        val = (mind, -opp_close, dx, dy)
        if best is None or val < best:
            best = val
            best_move = [dx, dy]
    return best_move
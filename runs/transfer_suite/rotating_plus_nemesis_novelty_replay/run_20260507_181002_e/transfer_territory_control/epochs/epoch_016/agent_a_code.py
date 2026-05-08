def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))
    remaining = observation.get("remaining_resource_count", None)
    if resources and isinstance(remaining, int) and remaining <= 0:
        resources = set()

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    x0y0 = (sx, sy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    target = None
    best = None
    if resources:
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = abs(rx - sx) + abs(ry - sy)
            if best is None or d < best or (d == best and (rx, ry) < target):
                best = d
                target = (rx, ry)
    if target is None:
        target = (ox, oy)

    best_move = None
    best_val = None
    for dx, dy, nx, ny in candidates:
        d_to_target = abs(target[0] - nx) + abs(target[1] - ny)
        d_to_opp = abs(ox - nx) + abs(oy - ny)
        val = (d_to_target, -d_to_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
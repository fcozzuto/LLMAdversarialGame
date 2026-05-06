def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    best = (sx, sy)
    bestv = None

    if resources:
        rs = []
        for r in resources:
            try:
                rx, ry = r
            except Exception:
                continue
            rs.append((rx, ry))
        rs.sort(key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
        target = rs[0] if rs else (w // 2, h // 2)
        oppt = rs[1] if len(rs) > 1 else (ox, oy)
    else:
        target = (w // 2, h // 2)
        oppt = (ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = man(nx, ny, target[0], target[1])
        do = man(nx, ny, ox, oy)
        if resources and target == (w // 2, h // 2):
            v = d * 10 + do
        else:
            # Prefer reducing distance to nearest resource; avoid getting too close to opponent
            v = d * 10 + (0 if resources and (nx, ny) == target else 0) + max(0, 3 - do) * 7
        if bestv is None or v < bestv or (v == bestv and (nx, ny) < best):
            bestv = v
            best = (nx, ny)

    return [best[0] - sx, best[1] - sy]
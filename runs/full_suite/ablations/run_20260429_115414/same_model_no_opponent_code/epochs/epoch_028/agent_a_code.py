def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    def parse_xy(v):
        try:
            x, y = v
            return int(x), int(y)
        except Exception:
            return None

    s = parse_xy(observation.get("self_position", (0, 0)))
    o = parse_xy(observation.get("opponent_position", (0, 0)))
    sx, sy = (s if s else (0, 0))
    ox, oy = (o if o else (0, 0))

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        xy = parse_xy(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else None
        if xy:
            x, y = xy
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        xy = parse_xy(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else None
        if xy:
            x, y = xy
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cur = (sx, sy)
    target = None
    if resources:
        target = min(resources, key=lambda r: (man(cur, r), r[1], r[0]))

    if target is not None:
        best = None
        bestk = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            k = (man((nx, ny), target), abs((nx - ox)) + abs((ny - oy)), dy, dx)
            if best is None or k < bestk:
                best = (dx, dy)
                bestk = k
        if best is not None:
            return [int(best[0]), int(best[1])]

    # Fallback: move to increase distance from opponent while avoiding obstacles
    best = (0, 0)
    bestk = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        k = (-man((nx, ny), (ox, oy)), dy, dx)
        if bestk is None or k < bestk:
            bestk = k
            best = (dx, dy)
    return [int(best[0]), int(best[1])]
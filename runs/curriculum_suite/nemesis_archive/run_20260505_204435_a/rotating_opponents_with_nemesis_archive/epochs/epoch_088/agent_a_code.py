def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    def cell(p):
        if isinstance(p, dict):
            p = p.get("position")
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return (int(p[0]), int(p[1]))
        return None

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for ob in obstacles:
        q = cell(ob)
        if q:
            blocked.add(q)

    resources = observation.get("resources", []) or []
    rlist = []
    for r in resources:
        q = cell(r)
        if q and 0 <= q[0] < w and 0 <= q[1] < h and q not in blocked:
            rlist.append(q)

    if not rlist:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = min(rlist, key=lambda q: (man((sx, sy), q), q[0], q[1]))

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = None
    bestd = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            d = man((nx, ny), target)
            v = (d, -((nx == ox and ny == oy)), nx, ny)
            if bestd is None or v < bestd:
                bestd = v
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
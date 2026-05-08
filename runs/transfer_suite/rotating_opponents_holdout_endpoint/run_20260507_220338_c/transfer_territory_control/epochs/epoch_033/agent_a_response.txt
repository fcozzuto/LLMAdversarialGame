def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in (observation.get("obstacles") or []):
        blocked.add((int(p[0]), int(p[1])))

    myset = set()
    for p in (observation.get("self_territory") or []):
        myset.add((int(p[0]), int(p[1])))

    oset = set()
    for p in (observation.get("opponent_territory") or []):
        oset.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        unclaimed.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources") or []):
        resources.append((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    edge_unclaimed = [c for c in unclaimed if c[0] in (0, w - 1) or c[1] in (0, h - 1)]
    use_edge = edge_unclaimed if edge_unclaimed else list(unclaimed)

    best = None
    best_val = -10**18
    for dx, dy, nx, ny in cand:
        val = 0
        if (nx, ny) in myset:
            val += 5
        elif (nx, ny) in unclaimed:
            val += 4
        elif (nx, ny) in oset:
            val += 9
        else:
            val += 1

        val += max(0, 6 - manh((nx, ny), (ox, oy)))  # move closer to pressure
        if use_edge:
            d_edge = min(manh((nx, ny), t) for t in use_edge)
            val += max(0, 5 - d_edge)
        if resources:
            d_res = min(manh((nx, ny), r) for r in resources)
            val += max(0, 4 - d_res)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
def choose_move(observation):
    W = observation.get("grid_width", 0) or 0
    H = observation.get("grid_height", 0) or 0
    try:
        W = int(W); H = int(H)
    except:
        W = 0; H = 0
    if W <= 0 or H <= 0:
        return [0, 0]

    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict) and ("x" in v and "y" in v):
            return int(v["x"]), int(v["y"])
        return 0, 0

    sx, sy = xy(observation.get("self_position", [0, 0]))
    opx, opy = xy(observation.get("opponent_position", [sx, sy]))

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for c in obstacles:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < W and 0 <= y < H:
                obs_set.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs_set

    resources = observation.get("resources", []) or []
    res = []
    for c in resources:
        x, y = xy(c)
        if inb(x, y):
            res.append((x, y))

    unclaimed = observation.get("unclaimed_cells", []) or []
    uc = []
    for c in unclaimed:
        x, y = xy(c)
        if inb(x, y):
            uc.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_to_opp = man((sx, sy), (opx, opy))

    target = None
    if res:
        candidates = []
        for r in res:
            ds = man((sx, sy), r)
            do = man((opx, opy), r)
            better = (1 if ds <= do else 0)
            candidates.append((better, ds, r[0], r[1], r))
        candidates.sort(reverse=True)
        target = candidates[0][4]
    elif uc:
        target = min(uc, key=lambda p: (man((sx, sy), p), p[0], p[1]))
    else:
        target = (W // 2, H // 2) if inb(W // 2, H // 2) else (sx, sy)

    best = (float("-inf"), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = man((nx, ny), target)
        d_to_o = man((nx, ny), (opx, opy))
        closer_opp = self_to_opp - d_to_o
        h = -d_to_t + (0 if (nx, ny) != target else 1000) - (2 * closer_opp if closer_opp > 0 else 0)
        if h > best[0]:
            best = (h, dx, dy)
    return [best[1], best[2]] if best[0] != float("-inf") else [0, 0]
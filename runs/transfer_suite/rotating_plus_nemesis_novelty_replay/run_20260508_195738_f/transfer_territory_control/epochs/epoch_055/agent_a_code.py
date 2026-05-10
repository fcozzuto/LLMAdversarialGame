def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict) and "x" in p and "y" in p:
            obs.add((int(p["x"]), int(p["y"])))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))
        elif isinstance(p, dict) and "x" in p and "y" in p:
            res.append((int(p["x"]), int(p["y"])))

    unclaimed = observation.get("unclaimed_cells", []) or []
    uc = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            uc.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_op = dist((nx, ny), (ox, oy))
        d_res = min((dist((nx, ny), r) for r in res), default=10**6)
        v = 0
        if (nx, ny) in uc:
            v += 20
        v += -d_res
        v += d_op * 0.5
        if (nx, ny) == (ox, oy):
            v += 1000
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
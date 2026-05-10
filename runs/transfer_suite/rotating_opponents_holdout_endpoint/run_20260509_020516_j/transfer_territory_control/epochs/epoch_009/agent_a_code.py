def choose_move(observation):
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    def xy(v, default=None):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
        return default

    sx_sy = xy(observation.get("self_position", (0, 0)), (0, 0))
    ox_oy = xy(observation.get("opponent_position", (0, 0)), (0, 0))
    sx, sy = sx_sy
    ox, oy = ox_oy

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for c in obstacles:
        t = xy(c)
        if t is not None:
            x, y = t
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    targets = []
    for key in ("resources", "remaining_resources"):
        if key in observation:
            for r in observation.get(key, []) or []:
                t = xy(r)
                if t is not None:
                    x, y = t
                    if ok(x, y):
                        targets.append((x, y))
            if targets:
                break
    if not targets:
        for r in observation.get("unclaimed_cells", []) or []:
            t = xy(r)
            if t is not None:
                x, y = t
                if ok(x, y):
                    targets.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if targets:
            d = min(man(nx, ny, tx, ty) for tx, ty in targets)
        else:
            d = man(nx, ny, ox, oy)
        score = d
        # Prefer moves that don't head directly toward opponent too aggressively
        score += 1 if man(nx, ny, ox, oy) <= 1 else 0
        # Tie-break deterministically by direction order
        cand = (score, dx, dy)
        if cand < best:
            best = cand

    return [best[1], best[2]]
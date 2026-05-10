def choose_move(observation):
    W = int(observation.get("grid_width") or 0)
    H = int(observation.get("grid_height") or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
        return 0, 0

    sx, sy = xy(observation.get("self_position") or (0, 0))
    ox, oy = xy(observation.get("opponent_position") or (0, 0))
    cx, cy = (W - 1) // 2, (H - 1) // 2

    obs = set()
    for p in (observation.get("obstacles") or []):
        x, y = xy(p)
        if 0 <= x < W and 0 <= y < H:
            obs.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        x, y = xy(p)
        if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
            resources.append((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        x, y = xy(p)
        if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
            unclaimed.append((x, y))

    def dist(a, b, x, y):
        return abs(x - a) + abs(y - b)

    target = None
    if resources:
        bestd = 10**18
        for tx, ty in resources:
            d = dist(sx, sy, tx, ty)
            if d < bestd:
                bestd = d
                target = (tx, ty)
    if target is None and unclaimed:
        bestv = -10**18
        for tx, ty in unclaimed:
            v = 3 * dist(sx, sy, tx, ty) + dist(ox, oy, tx, ty)
            if v < bestv or target is None:
                pass
        # Instead: pick far from opponent but not too far from us
        bestv = -10**18
        for tx, ty in unclaimed:
            v = -dist(sx, sy, tx, ty) + 2 * dist(ox, oy, tx, ty)
            v += -((abs(tx - cx) + abs(ty - cy)) // 2)
            if v > bestv:
                bestv = v
                target = (tx, ty)

    if target is None:
        target = (cx, cy)

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]
    best = None
    bestscore = -10**18
    tx, ty = target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obs:
            continue
        myd = dist(nx, ny, tx, ty)
        opdd = dist(nx, ny, ox, oy)
        score = -1000 * myd + 120 * opdd - 3 * dist(nx, ny, cx, cy)
        if score > bestscore:
            bestscore = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
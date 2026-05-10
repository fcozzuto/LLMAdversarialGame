def choose_move(observation):
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    sx, sy = xy(observation.get("self_position", [0, 0]))
    opx, opy = xy(observation.get("opponent_position", [sx, sy]))

    obs = set()
    for c in observation.get("obstacles", []) or []:
        x, y = xy(c)
        if 0 <= x < W and 0 <= y < H:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = observation.get("resources", None) or []
    targets = []
    for r in resources:
        x, y = xy(r)
        if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
            targets.append((x, y))
    if not targets and (observation.get("remaining_resource_count", 0) or 0) > 0:
        targets = [(opx, opy)]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        tval = 0
        if targets:
            m = min(d2(nx, ny, tx, ty) for tx, ty in targets)
            tval = m
        opp_close = d2(nx, ny, opx, opy)
        # Prefer closer to resources/target, then closer to opponent (to contest).
        val = (tval, opp_close, -(dx == 0 and dy == 0))
        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]
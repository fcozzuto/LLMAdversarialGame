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
    opx, opy = xy(observation.get("opponent_position", [0, 0]))
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    obs = set()
    for c in observation.get("obstacles", []) or []:
        x, y = xy(c)
        if 0 <= x < W and 0 <= y < H:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    resources = observation.get("resources", []) or []
    targets = []
    for c in resources:
        x, y = xy(c)
        if inb(x, y) and (x, y) not in obs:
            targets.append((x, y))

    def dist2(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        if targets:
            md = min(dist2(nx, ny, tx, ty) for tx, ty in targets)
            od = dist2(nx, ny, opx, opy)
            score = (0, md, -od, dx, dy)
        else:
            # No resources known: stay safe and drift toward center deterministically.
            cx = (W - 1) // 2
            cy = (H - 1) // 2
            od = dist2(nx, ny, opx, opy)
            cd = dist2(nx, ny, cx, cy)
            score = (-od, cd, 0, dx, dy)

        if best is None or score < best:
            best = score
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move
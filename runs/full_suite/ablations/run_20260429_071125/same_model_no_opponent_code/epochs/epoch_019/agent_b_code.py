def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
            p = v.get("position", None)
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return 0, 0

    sx, sy = xy(observation.get("self_position", [0, 0]))
    ox, oy = xy(observation.get("opponent_position", [0, 0]))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        x, y = xy(p)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        x, y = xy(p)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick a target resource that we can reach sooner than the opponent.
    target = None
    if resources:
        best = None
        for tx, ty in resources:
            myd = cheb(sx, sy, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer winning the race; if tie, prefer resource closer to us.
            score = (opd - myd) * 100 - myd
            if best is None or score > best:
                best = score
                target = (tx, ty)
    else:
        # No visible resources: move toward center-ish (but deterministically).
        target = (w // 2, h // 2)

    tx, ty = target
    myd0 = cheb(sx, sy, tx, ty)
    opd0 = cheb(ox, oy, sx, sy)

    # Choose the step that best improves our position vs target and keeps distance from opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        # Slightly avoid stepping near opponent unless it also helps us capture the target.
        nd_op = cheb(nx, ny, ox, oy)
        closer = (myd0 - myd)
        race = (cheb(ox, oy, tx, ty) - myd)
        val = closer * 50 + race * 2 + nd_op * 0.1
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
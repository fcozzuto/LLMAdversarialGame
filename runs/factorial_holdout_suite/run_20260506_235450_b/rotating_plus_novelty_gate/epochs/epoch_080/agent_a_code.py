def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    valid_resources = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                valid_resources.append((x, y))
    if not valid_resources:
        return [0, 0]

    # Choose a resource where we are closer than opponent; tie-break by smaller my distance.
    best = None
    best_key = None
    for x, y in valid_resources:
        myd = dist(sx, sy, x, y)
        opd = dist(ox, oy, x, y)
        key = (opd - myd, -myd)  # maximize advantage, then minimize my distance
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that reduce distance to target, also avoid getting closer to opponent's favored region by their distance.
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = dist(nx, ny, tx, ty)
        # Denial pressure: if opponent also approaches this target, slightly prefer staying ahead.
        opd = dist(ox, oy, tx, ty)
        v = (-(myd), myd - opd)  # primary: smaller myd; secondary: reduce myd-opd
        if bestv is None or v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]
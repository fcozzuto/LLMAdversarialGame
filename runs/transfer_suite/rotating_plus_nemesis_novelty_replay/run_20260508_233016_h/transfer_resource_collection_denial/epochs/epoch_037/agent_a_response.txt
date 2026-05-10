def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target I can reach not later than opponent; then prefer closer and more "contested" cells.
    best = None
    bestk = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # key: first prefer I arrive first (or tie), then minimize my distance,
        # then maximize opponent distance, then lexicographic by coordinate for determinism.
        k = (0 if myd <= opd else 1, myd, -opd, rx, ry)
        if bestk is None or k < bestk:
            bestk = k
            best = (rx, ry)
    tx, ty = best

    # Obstacle-aware greedy: choose move that most reduces distance to target while staying safe.
    def dist_after(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            return 10**9, 10**9, 10**9
        d_to = man(nx, ny, tx, ty)
        d_op = man(nx, ny, ox, oy)
        return d_to, -d_op, 0

    bestm = (0, 0)
    bestv = None
    for dx, dy in dirs:
        v = dist_after(dx, dy)
        if bestv is None or v < bestv:
            bestv = v
            bestm = (dx, dy)

    # If all safe moves are bad or blocked, try an axis step that stays free.
    if bestv is None or bestv[0] >= 10**8:
        candidates = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                candidates.append((man(nx, ny, tx, ty), nx, ny, dx, dy))
        if not candidates:
            return [0, 0]
        candidates.sort()
        return [candidates[0][3], candidates[0][4]]

    return [bestm[0], bestm[1]]
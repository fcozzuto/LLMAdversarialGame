def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(a, b, c, d):
        a -= c
        if a < 0: a = -a
        b -= d
        if b < 0: b = -b
        return a + b
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]
    ox, oy = observation.get("opponent_position", (0, 0))
    ox, oy = int(ox), int(oy)
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer resources we can reach at least as soon, and where we are advantaged.
        key = (-(sd <= od), -(od - sd), sd, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key
    tx, ty = best
    # Choose next move that reduces distance to target while staying valid.
    curd = md(sx, sy, tx, ty)
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = md(nx, ny, tx, ty)
        candidates.append((nd, dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda z: (z[0], abs(z[3] - ox) + abs(z[4] - oy), z[1], z[2]))
    if candidates[0][0] <= curd:
        return [candidates[0][1], candidates[0][2]]
    # If all increase, take least increase (deterministic).
    return [candidates[0][1], candidates[0][2]]
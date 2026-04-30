def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]) or [0, 0])
    ox, oy = map(int, observation.get("opponent_position", [0, 0]) or [0, 0])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cands = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cands.append((dx, dy, nx, ny))
    if not cands:
        return [0, 0]

    # Choose a target resource to contest: smaller my_dist and larger opp_dist helps.
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            md = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we can reach first; deterministic tie-break by position.
            score = (md - 0.65 * od, rx, ry)
            if best is None or score < best:
                best = score
                target = (rx, ry)

    # Evaluate each candidate: move closer to target while considering opponent pressure and local safety.
    best_move = None
    best_val = -10**18
    for dx, dy, nx, ny in cands:
        val = 0.0
        if target is not None:
            rx, ry = target
            md = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            val += -md * 1.0 + od * 0.35
            # Small bias to keep moving towards target diagonals (same parity step helps).
            val += -0.03 * (abs((nx + ny) - (sx + sy)))
        else:
            # No resources: drift toward center deterministically
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val += -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # Local safety: prefer moves with more available exits.
        exits = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if free(tx, ty):
                exits += 1
        val += exits * 0.12
        # Deterministic tie-break: lexicographic dx,dy
        if best_move is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
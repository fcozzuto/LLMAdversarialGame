def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, drift toward the center while avoiding obstacles.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (-(10**18), 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            sc = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Prefer resources we are closer to than the opponent; evaluate by local move.
    # Use only a few most promising resources for speed/determinism.
    scored = []
    for r in resources:
        d_me = dist((sx, sy), r)
        d_op = dist((ox, oy), r)
        # Higher is better: we want (d_op - d_me) and nearer targets.
        scored.append((d_me, -(d_op - d_me), r))
    scored.sort(key=lambda t: (t[0], t[1], t[2][0], t[2][1]))
    top = [t[2] for t in scored[:6]]

    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my = (nx, ny)
        # Main score: move that maximizes advantage over opponent for near targets.
        sc = 0
        for r in top:
            d1 = dist(my, r)
            d2 = dist((ox, oy), r)
            # Encourage taking quickly; discourage giving opponent easy access.
            sc += (d2 - d1) * 3 - d1
            # Small tie-break to stay efficient near our current line.
        # Deterministic tie-break: prefer smaller dx/dy lexicographically via fixed order
        if sc > best[0]:
            best = (sc, dx, dy)

    return [best[1], best[2]]
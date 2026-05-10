def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    if not unclaimed:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    my_corner = min(corners, key=lambda c: man(sx, sy, c[0], c[1]))
    cx, cy = my_corner

    # Prefer unclaimed that are "safer": far from opponent, not too far from us, and toward our corner/edges.
    best = None
    best_sc = None
    for p in unclaimed:
        x, y = int(p[0]), int(p[1])
        if not legal(x, y):
            continue
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        edge = 1 if (x == 0 or y == 0 or x == w - 1 or y == h - 1) else 0
        toward_corner = max(0, 7 - man(x, y, cx, cy))  # small bonus near our corner
        sc = (do - ds) + edge * 1.5 + toward_corner * 0.25
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (x, y)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for ddx, ddy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + ddx, sy + ddy
        if legal(nx, ny):
            candidates.append((ddx, ddy))

    # Choose deterministic best step that maximizes the same safety heuristic one move ahead.
    best_step = [0, 0]
    best_step_sc = None
    for ddx, ddy in candidates[:20]:
        nx, ny = sx + ddx, sy + ddy
        if not legal(nx, ny):
            continue
        ds = man(nx, ny, tx, ty)
        do = man(ox, oy, nx, ny)
        edge = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        toward_corner = max(0, 7 - man(nx, ny, cx, cy))
        sc = (do - ds) + edge * 1.5 + toward_corner * 0.25
        if best_step_sc is None or sc > best_step_sc:
            best_step_sc = sc
            best_step = [ddx, ddy]

    return best_step
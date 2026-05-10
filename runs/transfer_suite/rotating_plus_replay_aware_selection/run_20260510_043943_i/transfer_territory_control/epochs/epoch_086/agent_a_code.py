def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                unclaimed.append((x, y))
    if not unclaimed:
        for p in observation.get("opponent_territory") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if valid(x, y):
                    unclaimed.append((x, y))
    if not unclaimed:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    center = (cx, cy)
    best_cell = None
    best_key = None
    for x, y in unclaimed:
        # Prefer cells near center, but also prefer cells the opponent is not closest to.
        d_center = abs(x - center[0]) + abs(y - center[1])
        d_opp = man((x, y), (ox, oy))
        # Deterministic tie-break: lexicographic on (x,y)
        key = (d_center, -d_opp, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best_cell = (x, y)

    tx, ty = best_cell
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal/step hits obstacle, fall back to best among valid 8-neighborhood moves.
    cand = []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if valid(nx, ny):
            # Move to reduce distance to target, with a bias away from opponent.
            score = -man((nx, ny), (tx, ty)) + 0.2 * man((nx, ny), (ox, oy))
            cand.append((score, nx, ny))
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    if cand:
        _, nx, ny = cand[0]
        return [nx - sx, ny - sy]
    return [0, 0]
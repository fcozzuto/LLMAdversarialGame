def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    same_row_pen = 3.0  # discourage contested row for sweep-like opponent
    best_key = None
    best = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        advantage = od - sd  # larger is better
        row_pen = same_row_pen if ry == oy else 0.0
        # Prefer faster pickup for us, and prefer resources far from opponent row (to avoid row sweep)
        key = (advantage - row_pen, -sd, -od, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                nd = max(abs(nx - tx), abs(ny - ty))
                candidates.append((nd, dx, dy))
    if not candidates:
        return [0, 0]

    # Choose the move that makes our progress fastest; break ties by keeping off opponent row.
    best_m = None
    best_m_key = None
    for nd, dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        row_term = 1 if ny == oy else 0
        mkey = (-nd, -row_term, dx, dy)  # smallest nd is best => maximize -nd
        if best_m_key is None or mkey > best_m_key:
            best_m_key = mkey
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]
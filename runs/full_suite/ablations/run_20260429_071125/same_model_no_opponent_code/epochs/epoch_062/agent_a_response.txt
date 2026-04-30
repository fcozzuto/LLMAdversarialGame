def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for r in resources:
        myd = cd((sx, sy), r)
        opd = cd((ox, oy), r)
        # Prefer being earlier; then closer; then deterministic tie by position
        key = (myd - opd, myd, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_r = r

    tx, ty = best_r
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    candidates.append((dx, dy))
    if dx != 0 or dy != 0:
        candidates.append((dx, 0))
        candidates.append((0, dy))
        candidates.append((-dx, dy))
        candidates.append((dx, -dy))
    candidates.append((0, 0))

    for mdx, mdy in candidates:
        nx, ny = sx + mdx, sy + mdy
        if inb(nx, ny):
            return [int(mdx), int(mdy)]

    return [0, 0]
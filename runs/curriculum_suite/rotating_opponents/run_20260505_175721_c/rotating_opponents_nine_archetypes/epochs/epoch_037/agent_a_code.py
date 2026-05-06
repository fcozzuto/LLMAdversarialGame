def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
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

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def res_key(tx, ty):
        myd = man(sx, sy, tx, ty)
        opd = man(ox, oy, tx, ty)
        margin = opd - myd
        center_bias = - (abs(tx - cx) + abs(ty - cy)) * 0.01
        return (margin, -myd, center_bias)

    resources.sort(key=lambda t: res_key(t[0], t[1]), reverse=True)
    tx, ty = resources[0]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # prefer improving our distance, and also preventing opponent from getting closer
        score = (opd - myd, -myd, -(abs(nx - cx) + abs(ny - cy))*0.01, -abs(nx - ox) - abs(ny - oy)*0.001)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
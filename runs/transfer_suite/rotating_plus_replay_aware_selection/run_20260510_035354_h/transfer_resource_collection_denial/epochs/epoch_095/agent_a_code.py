def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def sign(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    # Pick a resource we can reach earlier than opponent (tie-break by closeness).
    best = None
    bestk = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        k = (do - ds, -ds, rx, ry)  # prefer positive advantage, then nearer
        if bestk is None or k > bestk:
            bestk = k
            best = (rx, ry)

    tx, ty = best

    # Evaluate one-step moves, avoid obstacles/off-grid, favor reducing distance to target
    # and maintaining advantage vs opponent.
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            ns = man(nx, ny, tx, ty)
            no = man(ox, oy, tx, ty)
            opp_step_bias = man(ox, oy, tx, ty) - no
            # Primary: maximize advantage against opponent; Secondary: minimize our distance.
            score = (no - ns, -ns, -opp_step_bias, -abs(nx - tx) - abs(ny - ty), nx, ny)
            cand.append((score, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]
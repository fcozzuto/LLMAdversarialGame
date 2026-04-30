def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if valid(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    best = None
    best_key = None
    for rx, ry in resources:
        du = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Prefer positions we can reach sooner than opponent; also prefer closer absolute distance.
        key = (du - do, du, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    # Choose move that minimizes resulting "du-do" for the selected target, with deterministic tie-break.
    best_move = None
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        du = md(nx, ny, rx, ry)
        do = md(ox, oy, rx, ry)
        key = (du - do, du, abs(nx - ox) + abs(ny - oy), dx, dy, nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = [dx, dy]
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If no resources visible, bias toward center-ish while keeping safe.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            d = man(nx, ny, cx, cy)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Opponent best possible distance to a target next turn.
    def opp_best_next(tx, ty):
        bestd = 10**9
        for dpx, dpy in dirs:
            nx, ny = ox + dpx, oy + dpy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                dd = man(nx, ny, tx, ty)
                if dd < bestd:
                    bestd = dd
        return bestd if bestd != 10**9 else man(ox, oy, tx, ty)

    best_move = None
    best_key = None
    # Deterministic lex tie-break: prefer smaller dx then dy.
    for dx, dy, nx, ny in moves:
        myd = 10**9
        score = -10**9
        for tx, ty in resources:
            d_my = man(nx, ny, tx, ty)
            d_op = opp_best_next(tx, ty)
            # Primary: maximize advantage (opponent further than me after my move).
            # Secondary: choose closer overall when advantage ties.
            adv = d_op - d_my
            s = adv * 100 - d_my
            if s > score or (s == score and (d_my < myd or (d_my == myd and (dx, dy) < (best_move[0], best_move[1])))):
                score = s
                myd = d_my
        key = (-score, myd, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
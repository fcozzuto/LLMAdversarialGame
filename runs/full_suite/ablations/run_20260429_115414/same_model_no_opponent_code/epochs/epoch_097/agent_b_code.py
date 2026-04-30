def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    # Choose a target deterministically: nearest resource; tie-break by x then y.
    target = None
    if resources:
        best = (10**9, 10**9, 10**9)
        for (tx, ty) in resources:
            d = king_dist(sx, sy, tx, ty)
            key = (d, tx, ty)
            if key < best:
                best = key
                target = (tx, ty)
    else:
        target = ((w - 1) // 2, (h - 1) // 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    move_order = sorted(moves, key=lambda d: (d[0], d[1]))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_t = king_dist(nx, ny, target[0], target[1])
        d_o = king_dist(nx, ny, ox, oy)

        # Resource race: if we can reach/approach a closer point than opponent, prefer it.
        if resources:
            min_r = 10**9
            for (rx, ry) in resources:
                if ok(rx, ry):
                    dr = king_dist(nx, ny, rx, ry)
                    if dr < min_r:
                        min_r = dr
            d_op = 10**9
            for (rx, ry) in resources:
                if ok(rx, ry):
                    d2 = king_dist(ox, oy, rx, ry)
                    if d2 < d_op:
                        d_op = d2
            race = d_op - min_r
        else:
            race = 0

        # Heuristics:
        # - primary: decrease distance to target (or center when no resources)
        # - secondary: avoid getting closer to opponent
        # - tertiary: win resource races
        score = (-d_t) + (0.35 * d_o) + (2.0 * race)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score and (dx, dy) < best_move:
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
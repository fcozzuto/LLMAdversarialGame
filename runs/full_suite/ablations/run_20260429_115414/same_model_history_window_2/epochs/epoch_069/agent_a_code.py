def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry):
                res.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free_nbrs(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    if not res:
        best = (-(free_nbrs(sx, sy)), 0)
        bx, by = sx, sy
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            sc = (free_nbrs(nx, ny), -cheb(nx, ny, ox, oy))
            if sc > best[0:1] or bx == sx and by == sy:
                bx, by = nx, ny
        return [bx - sx, by - sy]

    # Choose a deterministic target: closest resource; tie by lexicographic.
    best_t = None
    best_d = None
    for rx, ry in res:
        d = cheb(sx, sy, rx, ry)
        if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_t):
            best_d = d
            best_t = (rx, ry)
    tx, ty = best_t

    best_move = (0, 0)
    best_score = -10**18

    # Candidate scoring: move that most reduces distance to target.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_next = cheb(nx, ny, tx, ty)
        d_now = cheb(sx, sy, tx, ty)

        # Contention penalty if opponent is closer to the target than we are after moving.
        opp_d = cheb(ox, oy, tx, ty)
        cont = 0
        if opp_d < d_next:
            cont = 1

        # Exploration bonus: free neighbors.
        fn = free_nbrs(nx, ny)

        # Small deterministic tie-breaker: prefer moves that are lexicographically smaller (dx,dy).
        lex = -(dx * 3 + (dy + 1))

        score = (d_now - d_next) * 10 - cont * 3 + fn * 0.2 + lex * 1e-6
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score and (dx, dy) < best_move:
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
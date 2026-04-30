def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        b = y1 - y2
        if a < 0: a = -a
        if b < 0: b = -b
        return a if a > b else b

    def neigh_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    if resources:
        # pick a target resource that is good for us and not too close to opponent
        best_t = None
        best_s = -10**18
        for (rx, ry) in resources:
            if not valid(rx, ry):
                continue
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # if opponent is closer, deprioritize; otherwise favor.
            score = (d_op - d_me) * 100 - d_me * 3 + neigh_count(rx, ry)
            # slight tie-break to stable ordering by coordinates
            score += -(rx * 0.001 + ry * 0.000001)
            if score > best_s:
                best_s = score
                best_t = (rx, ry)
        if best_t is None:
            best_t = (min(resources)[0], min(resources)[1])
    else:
        best_t = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = best_t
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_new = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)

        # Encourage moving toward target, keep distance from opponent, and maintain mobility.
        val = -d_new * 12 + d_op * 2 + neigh_count(nx, ny)

        # If we can "contest" opponent by getting nearer to target than opponent is.
        op_to_t = cheb(ox, oy, tx, ty)
        if d_new < op_to_t:
            val += 50

        # Small deterministic preference to reduce oscillation: prefer axes over diagonals when equal.
        if val == best_val:
            prefer = (0 if dx == 0 or dy == 0 else 1, dx, dy)
            bprefer = (0 if best_move[0] == 0 or best_move[1] == 0 else 1, best_move[0], best_move[1])
            if prefer < bprefer:
                best_move = (dx, dy)
        elif val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]
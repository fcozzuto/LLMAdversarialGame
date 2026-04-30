def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles:
                        c += 1
        return c

    # Pick target: maximize (opp_advantage - our_distance) and prefer targets closer to us.
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # If opponent is already closer, penalize strongly.
        clos_pen = 20 if opd < myd else 0
        # Encourage capturing near us while denying opponent.
        score = (opd - myd) - 0.15 * myd - clos_pen
        # Deterministic tie-break: prefer lexicographically smaller target.
        key = (score, -myd, -opd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Evaluate our legal moves: prefer reducing distance to target; also avoid stepping next to obstacles.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Secondary preference: if we can reach target immediately, do it.
    dist_now = cheb(sx, sy, tx, ty)

    best = None
    best_key = None
    for dx, dy, nx, ny in moves:
        d1 = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # If we move closer, good; if not, worse. Also keep away from obstacles.
        key = (
            100000 if d1 == 0 else 0,
            -(d1 - dist_now),
            (opp_d - d1),
            -adj_obst(nx, ny),
            -cheb(ox, oy, nx, ny),  # keep a bit away from opponent
            -nx,
            -ny
        )
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_near(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            nx = x + ddx
            if nx < 0 or nx >= w:
                continue
            for ddy in (-1, 0, 1):
                ny = y + ddy
                if 0 <= ny < h and (nx, ny) in obstacles:
                    if not (nx == x and ny == y):
                        c += 1
        return c

    if not res:
        return [0, 0]

    # Choose target deterministically: minimize our effective cost while deprioritizing resources opponent can reach quickly.
    best = None
    best_cost = None
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If opponent is close, slightly prefer resources that we can arrive not later than them.
        lead = do - ds  # positive means we are closer
        near = obst_near(rx, ry)
        # Base: prioritize small ds; penalize being behind; penalize obstacle density.
        cost = ds + 0.6 * near + (0.8 if lead < 0 else 0.0) * (abs(lead) + 1)
        # Tie-break: prefer higher lead, then deterministic position order.
        key = (cost, -lead, rx, ry)
        if best is None or key < best[0]:
            best = ((cost, -lead, rx, ry), (rx, ry))
            best_cost = cost

    tx, ty = best[1]

    # Move one step: among legal deltas, choose one that reduces distance to target,
    # avoids obstacles/nearby blocks, and slightly increases distance from opponent.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                ds2 = cheb(nx, ny, tx, ty)
                do2 = cheb(nx, ny, ox, oy)
                near = obst_near(nx, ny)
                # Prefer smaller ds2, then larger do2, then fewer nearby obstacles, deterministic tie by (dx,dy).
                score = (ds2, -do2, near, dx, dy)
                moves.append((score, [dx, dy]))
    moves.sort(key=lambda x: x[0])

    return moves[0][1]
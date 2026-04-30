def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    target = None
    if resources:
        best_r = None
        best_gap = None
        for tx, ty in resources:
            myd = man(sx, sy, tx, ty)
            opd = man(ox, oy, tx, ty)
            gap = opd - myd  # positive means we are closer
            key = (gap, -myd, -tx, -ty)
            if best_gap is None or key > best_r:
                best_gap = key
                best_r = key
                target = (tx, ty)
        if best_r and best_gap[0] < 0:
            # we're behind everywhere; choose resource that minimizes our distance but avoid giving opponent an immediate grab
            target = min(resources, key=lambda r: (man(sx, sy, r[0], r[1]), -r[0], -r[1]))
    else:
        target = (ox, oy)

    tx, ty = target[0], target[1]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Since opponent position is static for this move, penalize giving them a quicker path via "relative" distance at our next move.
        # Also encourage progress: reduce both our distance and our distance to opponent.
        rel = (opd - myd)
        dist_to_op = man(nx, ny, ox, oy)
        score = (rel * 100) - myd * 3 + dist_to_op * 0.2
        # obstacle-local: slightly prefer not moving into tight corners
        tight = 0
        for adx, ady in ((-1,0),(1,0),(0,-1),(0,1)):
            ax2, ay2 = nx + adx, ny + ady
            if not (0 <= ax2 < W and 0 <= ay2 < H) or (ax2, ay2) in obstacles:
                tight += 1
        score -= tight * 0.5
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
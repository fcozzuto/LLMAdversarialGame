def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
    else:
        tx, ty = resources[0]
        best = None
        for (x, y) in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            # Prefer closer to us, also prefer farther from opponent; deterministic tie-break by coord.
            val = (-ds) * 10 + do
            key = (val, -x, -y)
            if best is None or key > best:
                best = key
                tx, ty = x, y

    # If opponent is adjacent to our target, bias to a safer detour by increasing distance from opponent.
    target_adj = (cheb(sx, sy, ox, oy) <= 1)

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist_to_target = cheb(nx, ny, tx, ty)
        dist_from_op = cheb(nx, ny, ox, oy)
        # Small penalty for moving away from target too much; reward safety and staying on board.
        score = (-dist_to_target) * 10 + dist_from_op
        if target_adj:
            score += dist_from_op * 3
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying still.
        tie = (-abs(dx) - abs(dy), -(dx + 1) * 100 - (dy + 1) * 10, -1 if (dx == 0 and dy == 0) else 0)
        total = (score, tie)
        if best_score is None or total > best_score:
            best_score = total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, head toward opponent (or just toward center if that would be blocked).
    if not resources:
        tx, ty = (ox, oy)
    else:
        # Pick best resource by deterministic advantage: prefer where we are at least as close as opponent.
        best = None
        best_score = -10**18
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Strongly prefer resources we can reach no later than opponent; then prefer smaller my distance.
            score = (opd - myd) * 1000 - myd
            if (rx, ry) == (sx, sy):
                score += 10**7
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best

    # Choose best legal immediate move toward target with deterministic tie-break.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        val = (opd - myd) * 1000 - myd
        # Secondary: keep moving if it improves toward target.
        if (nx, ny) == (tx, ty):
            val += 10**7
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    if not inb(sx, sy):
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy, nx, ny in legal_moves:
            score = (0, -cheb(nx, ny, ox, oy))
            if best is None or score > best[0]:
                best = (score, [dx, dy])
        return best[1]

    # Pick target where we have the best "advantage" in time to reach it.
    best_target = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer being closer; also prefer targets opponent is far from.
        val = (od - sd, -sd, rx, ry)
        if best_target is None or val > best_target[0]:
            best_target = (val, (rx, ry))
    tx, ty = best_target[1]

    # One-step lookahead: minimize our distance to target; add small tie-breaker for blocking proximity.
    best_move = None
    for dx, dy, nx, ny in legal_moves:
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # If we're equally good on distance, try to get closer to the opponent (deny captures).
        tieb = -cheb(nx, ny, ox, oy)
        # Also avoid moves that would give the opponent a huge advantage next step relative to us.
        next_adv = (opd - myd)
        score = (-myd, next_adv, tieb, dx, dy)
        if best_move is None or score > best_move[0]:
            best_move = (score, [dx, dy])
    return best_move[1]
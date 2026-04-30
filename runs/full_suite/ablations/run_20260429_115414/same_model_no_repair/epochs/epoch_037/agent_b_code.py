def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick the best contested resource: prioritize where we are earlier vs opponent.
    target = None
    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in blocked:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Strongly prefer being earlier; secondarily prefer smaller our distance.
        key = (do - ds, -ds, -rx, -ry)
        if best is None or key > best:
            best = key
            target = (rx, ry)

    if target is None:
        return [0, 0]
    tx, ty = target

    # Choose the move that maximizes immediate advantage around target,
    # while keeping us on-board and not walking into obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)

        # Encourage reducing our distance, and pushing opponent further (relative advantage).
        # Also add small tie-breakers for progress along target direction.
        dir_bonus = 0
        if nx != tx:
            dir_bonus += 1 if (tx > nx) == (dx > 0) else 0
        if ny != ty:
            dir_bonus += 1 if (ty > ny) == (dy > 0) else 0
        score = (opd - myd) * 10 - myd + dir_bonus * 0.2

        # Deterministic tie-break: prefer lower move lexicographically after score.
        mv_key = (score, -cheb(nx, ny, tx, ty), -nx, -ny, dx, dy)
        if best_score is None or mv_key > best_score:
            best_score = mv_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
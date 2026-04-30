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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    # Pick best resource to "claim": prefer those closer than opponent.
    tx, ty = None, None
    if resources:
        best = None
        for (rx, ry) in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Deterministic tie-breaking with (rx,ry)
            score = (do - ds) * 10 - ds
            cand = (score, -do, -ds, rx, ry)
            if best is None or cand > best:
                best = cand
        tx, ty = best[3], best[4]
    else:
        tx, ty = (W - 1) / 2.0, (H - 1) / 2.0

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if resources:
            d1 = cheb(nx, ny, tx, ty)
            d2 = cheb(nx, ny, ox, oy)
            # Encourage reducing distance to target while keeping separation.
            val = (-d1 * 5) + (d2 * 0.3)
            tie = (-cheb(ox, oy, tx, ty), -cheb(ox, oy, nx, ny), nx, ny)
            cand = (val, tie)
        else:
            dtx = cheb(nx, ny, tx, ty)
            cand = (-dtx, nx, ny)
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
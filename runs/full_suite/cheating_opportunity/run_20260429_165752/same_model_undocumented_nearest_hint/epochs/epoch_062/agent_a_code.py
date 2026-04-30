def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        tx, ty = ox, oy
    else:
        best = None
        best_score = None
        for tx, ty in res:
            d_me = cheb(sx, sy, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # Prefer smaller d_me; then larger lead over opponent; then earlier opponent is worse
            score = (d_me, -(d_op - d_me), d_me - d_op)
            if best is None or score < best_score:
                best, best_score = (tx, ty), score
        tx, ty = best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = 0
        d_me = cheb(nx, ny, tx, ty)
        v -= d_me * 100
        if res:
            # If moving onto a resource cell, heavily favor it
            if (nx, ny) in res:
                v += 1000000
        d_op = cheb(ox, oy, tx, ty)
        # Maintain lead or improve it
        v += (d_op - d_me) * 100
        if best_val is None or v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]
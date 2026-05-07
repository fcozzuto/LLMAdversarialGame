def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        for tx, ty in resources:
            d1 = cheb(sx, sy, tx, ty)
            d2 = cheb(ox, oy, tx, ty)
            closer = 0 if d1 <= d2 else 1
            key = (closer, d1, tx, ty)
            if best is None or key < best[0]:
                best = (key, tx, ty)
        _, tx, ty = best
        best_move = None
        for dx, dy, nx, ny in legal:
            cur = cheb(nx, ny, tx, ty)
            dcur = cheb(sx, sy, tx, ty)
            prog = dcur - cur
            # Prefer progress; then deterministically prefer x toward target, then y.
            key = (-prog, cur, abs(nx - tx), abs(ny - ty), -dx * (1 if tx > sx else -1 if tx < sx else 0), -dy * (1 if ty > sy else -1 if ty < sy else 0))
            if best_move is None or key < best_move[0]:
                best_move = (key, dx, dy)
        return [int(best_move[1]), int(best_move[2])]

    # No visible resources: head toward opponent's corner along Chebyshev.
    tx = w - 1 if ox == 0 else 0
    ty = h - 1 if oy == 0 else 0
    best_move = None
    for dx, dy, nx, ny in legal:
        cur = cheb(nx, ny, tx, ty)
        key = (cur, abs(nx - tx), abs(ny - ty), -dx, -dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)
    return [int(best_move[1]), int(best_move[2])]
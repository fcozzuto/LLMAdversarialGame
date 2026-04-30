def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for tx, ty in resources:
            dself = cheb(sx, sy, tx, ty)
            dop = cheb(ox, oy, tx, ty)
            # Prefer resources we can reach no later than opponent; otherwise pick one where we are relatively closer.
            if dself <= dop:
                key = (0, dself, cheb(tx, ty, (w - 1) // 2, (h - 1) // 2))
            else:
                key = (1, dself - dop, dself, dop)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Greedy step toward chosen target; if tied, move to increase separation from opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy, nx, ny in cand:
        d_to = cheb(nx, ny, tx, ty)
        sep = cheb(nx, ny, ox, oy)
        val = (d_to, -sep, abs(nx - tx) + abs(ny - ty))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
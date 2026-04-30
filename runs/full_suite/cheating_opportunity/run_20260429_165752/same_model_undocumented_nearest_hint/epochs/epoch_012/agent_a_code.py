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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose target resource you are relatively closer to, while opponent is relatively farther.
    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (ds - 0.65 * do, ds, -do)  # primary: advantage; then closer; then farther opponent
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t

        # Evaluate next move: minimize self distance; maximize opponent distance to target; avoid obstacles already ensured.
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Small bias: prefer not moving toward opponent when ds ties.
            da = cheb(nx, ny, ox, oy)
            key = (ds, -do, -da)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        if best:
            return [int(best[1][0]), int(best[1][1])]

    # No visible resources: reposition toward center, but keep away from opponent.
    cx, cy = (W - 1) // 2, (H - 1) // 2
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dc = cheb(nx, ny, cx, cy)
        da = cheb(nx, ny, ox, oy)
        key = (dc, -da)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    if best:
        return [int(best[1][0]), int(best[1][1])]
    return [0, 0]
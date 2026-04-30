def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [W - 1, H - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_tx, best_ty = resources[0]
        best_v = -10**18
        for tx, ty in resources:
            d_me = cheb(sx, sy, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            v = (d_op - d_me) * 1000 - d_me
            if v > best_v:
                best_v = v
                best_tx, best_ty = tx, ty
        tx, ty = best_tx, best_ty
    else:
        # No visible resources: drift toward opponent corner
        tx, ty = (W - 1, H - 1)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_me_now = cheb(nx, ny, tx, ty)
        d_op_now = cheb(ox, oy, tx, ty)
        # primary: become closer to our chosen target than opponent
        score = (d_op_now - d_me_now) * 1000 - d_me_now
        # secondary: small bias to reduce distance quickly
        score -= abs(nx - tx) + abs(ny - ty) * 0.001
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
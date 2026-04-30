def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [W - 1, H - 1]
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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
    else:
        center = ((W - 1) // 2, (H - 1) // 2)
        tx, ty = resources[0]
        best = None
        for x, y in resources:
            my_d = cheb(sx, sy, x, y)
            op_d = cheb(ox, oy, x, y)
            adv = op_d - my_d  # higher means we are relatively closer
            tie = -(abs(x - center[0]) + abs(y - center[1]))
            # prefer larger adv, then closer (smaller my_d), then deterministic coord
            key = (adv, tie, -my_d, -x, -y)
            if best is None or key > best:
                best = key
                tx, ty = x, y

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        my_d2 = cheb(nx, ny, tx, ty)
        op_d2 = cheb(ox, oy, tx, ty)
        # prioritize moving closer; if equal, avoid giving opponent relative advantage; deterministic tie-break
        key = (-my_d2, (op_d2 - my_d2), -abs(nx - tx) - abs(ny - ty), -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]
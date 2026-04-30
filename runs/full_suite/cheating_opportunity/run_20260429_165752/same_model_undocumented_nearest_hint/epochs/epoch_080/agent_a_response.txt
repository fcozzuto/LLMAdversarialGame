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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        target = min(resources, key=lambda t: cheb(sx, sy, t[0], t[1]))
        tx, ty = target[0], target[1]
    else:
        tx, ty = (W // 2), (H // 2)

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_res = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)

        # Prefer reaching resources while keeping distance from opponent.
        val = (-d_res) + 0.55 * d_opp

        # Mild bias to avoid getting stuck near obstacles: prefer moves with more escape options.
        free = 0
        for adx, ady in moves:
            ex, ey = nx + adx, ny + ady
            if ok(ex, ey):
                free += 1
        val += 0.02 * free

        # Deterministic tie-break by move order.
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
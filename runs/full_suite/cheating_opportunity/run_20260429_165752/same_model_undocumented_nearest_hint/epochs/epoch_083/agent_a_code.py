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

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        tx, ty = min(resources, key=lambda t: cheb(sx, sy, t[0], t[1])) if not (sx, sy) in resources else min(
            [t for t in resources if t != (sx, sy)] or resources,
            key=lambda t: cheb(sx, sy, t[0], t[1])
        )
    else:
        tx, ty = W // 2, H // 2

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        val = (op_d - my_d) * 100
        if resources:
            val += 2 if (nx, ny) in resources else 0
            val -= 1 if (nx, ny) in obstacles else 0
        # Slight preference for moving away from opponent when my distance is not improving much
        cur_my_d = cheb(sx, sy, tx, ty)
        if my_d >= cur_my_d:
            val -= cheb(nx, ny, ox, oy)
        else:
            val += 1
        # Deterministic tie-break: lexicographic on (dx, dy) after preferring higher val
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if not inside(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]
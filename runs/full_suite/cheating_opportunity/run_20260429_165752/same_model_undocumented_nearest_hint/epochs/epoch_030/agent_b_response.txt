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

    def free(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If no resources known, retreat to reduce opponent progress; otherwise contest a resource.
    if not resources:
        best_dxdy = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)  # maximize distance from opponent
            if v > bestv:
                bestv = v
                best_dxdy = (dx, dy)
        return [best_dxdy[0], best_dxdy[1]]

    # Choose contested target deterministically: prefer resources we are closer to; if none, take resource that is closest to opponent.
    target = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # key: primary minimize our distance advantage deficit (negative means we are behind), secondary prioritize reducing opponent access
        key = (-(do - ds), ds, do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    tx, ty = target
    my_dist = cheb(sx, sy, tx, ty)
    op_dist = cheb(ox, oy, tx, ty)

    # If we are behind, weight moving closer to target more but also slightly increase distance from opponent.
    behind = 1 if op_dist < my_dist else 0

    best_dxdy = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dtarget = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)
        # score: maximize (negative target distance) and (positive separation when behind)
        score = -dtarget * 10
        if behind:
            score += dop * 2
        else:
            score += -dtarget * 2 + dop // 4
        if score > bestv:
            bestv = score
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]
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

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        bestm, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            adv = cheb(nx, ny, ox, oy)  # stay away a bit
            v = -d + 0.05 * adv
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    # Choose move that improves our relative closeness to resources
    bestm, bestv = (0, 0), -10**18
    opp_d0 = 0.0
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue
        v = -0.01 * (abs(ox - nx) + abs(oy - ny))  # mild penalty toward opponent
        # evaluate best resource to target after the move
        best_rel = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # higher when we are closer than opponent
            rel = (do - ds) - 0.25 * ds
            if rel > best_rel:
                best_rel = rel
        v += best_rel
        # small deterministic preference to reduce oscillation: prefer moves that change direction toward target side
        if best_rel == -10**18:
            v = -10**18
        if v > bestv:
            bestv, bestm = v, (dxm, dym)

    return [bestm[0], bestm[1]]
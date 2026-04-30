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

    def obstacle_adj_penalty(nx, ny):
        # Small penalty for moving next to obstacles to reduce getting trapped
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in obstacles:
                    p += 1
        return p

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        bestm, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - 0.1 * obstacle_adj_penalty(nx, ny)
            if v > bestv:
                bestv, bestm = v, [dx, dy]
        return bestm

    # Evaluate each move by how much we "out-race" the opponent to remaining resources.
    bestm, bestv = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_best_diff = -10**9
        my_best_dist = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            diff = opd - myd  # positive means we are closer than opponent at this step
            if diff > my_best_diff:
                my_best_diff = diff
            if myd < my_best_dist:
                my_best_dist = myd
        # Also consider staying away from opponent when we can't secure an advantage.
        opp_sep = cheb(nx, ny, ox, oy)
        v = 50.0 * my_best_diff - 1.0 * my_best_dist + 0.5 * opp_sep - 0.25 * obstacle_adj_penalty(nx, ny)
        # Mild preference for moving generally toward the "most advantaged" resource.
        # Deterministic tiebreak by move order.
        if v > bestv:
            bestv, bestm = v, [dx, dy]
    return bestm
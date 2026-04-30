def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # If any resource is already within immediate step and unblocked, go for the best one.
    best_immediate = None
    best_immediate_d = 10**9
    for tx, ty in resources:
        d = cheb(sx, sy, tx, ty)
        if d == 0:
            best_immediate = (tx, ty)
            break
        if d == 1:
            if d < best_immediate_d:
                best_immediate_d = d
                best_immediate = (tx, ty)
    if best_immediate is not None:
        tx, ty = best_immediate
        # Prefer move that reduces distance to that target the most.
        best_move = (0, 0)
        best = -10**18
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not valid(nx, ny):
                continue
            nd = cheb(nx, ny, tx, ty)
            score = -nd * 10 + (-cheb(ox, oy, tx, ty))  # also slightly care about opponent
            if score > best:
                best = score
                best_move = (dxm, dym)
        return [int(best_move[0]), int(best_move[1])]

    # Main heuristic: choose move maximizing (opp_distance - our_distance) to a target.
    # Positive means we can arrive no later than opponent at that resource.
    best_move = (0, 0)
    best_val = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        our_best = -10**18
        for tx, ty in resources:
            d_our = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # Encourage capturing (d_our small) and denying (d_opp - d_our large).
            # Add tiny tie-break on target position deterministically.
            tie = -(tx * 17 + ty) * 1e-6
            val = (d_opp - d_our) * 2.0 - d_our * 0.25 + tie
            if val > our_best:
                our_best = val
        # If we can't get ahead, still prefer minimizing distance to the best target for us.
        if our_best > best_val + 1e-12:
            best_val = our_best
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]
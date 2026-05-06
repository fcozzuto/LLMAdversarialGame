def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        # Create deterministic separation by moving to maximize chebyshev distance.
        bestd = -10**9
        best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            d = cheb(nx, ny, ox, oy)
            if d > bestd or (d == bestd and (dx, dy) > best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Opponent likely targets nearest resource by manhattan.
    target = resources[0]
    bestm = manh(ox, oy, target[0], target[1])
    for rx, ry in resources[1:]:
        m = manh(ox, oy, rx, ry)
        if m < bestm:
            bestm = m
            target = (rx, ry)

    # Choose move that secures a resource with advantage; otherwise disrupt opponent's target.
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Evaluate best resource for us from next position.
        best_u = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Advantage: we prefer being closer than opponent; also prefer actual closeness.
            u = (d_opp - d_self) * 10 - d_self
            if u > best_u:
                best_u = u

        # If no advantage, bias toward denying opponent's nearest target.
        d_to_target = cheb(nx, ny, target[0], target[1])
        u_block = -d_to_target - manh(nx, ny, target[0], target[1]) * 0.1

        score = best_u + (best_u < 0) * 5 + (best_u >= 0) * 0 + u_block * (best_u < 0)
        if score > best_score or (score == best_score and (dx, dy) > best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
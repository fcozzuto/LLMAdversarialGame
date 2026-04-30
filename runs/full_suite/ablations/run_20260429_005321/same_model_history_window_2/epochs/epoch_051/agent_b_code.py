def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # 1-step lookahead: choose the move that creates the best "secure" advantage.
    # Secure score: prefer closing to targets quickly, and pushing opponent away.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        cur_best = -10**18
        for tx, ty in resources:
            d_me = cheb(nx, ny, tx, ty)
            d_op = cheb(ox, oy, tx, ty)

            # If we can capture immediately, prioritize heavily.
            if d_me == 0:
                sc = 10**12
            else:
                # Prefer targets where we are closer than opponent, otherwise still move toward nearer ones.
                # Use chebyshev distance; avoid division with simple scaling.
                closer = d_op - d_me
                sc = closer * 1000 - d_me * 10 + d_op * 1

            if sc > cur_best:
                cur_best = sc

        if cur_best > best_score:
            best_score = cur_best
            best_move = (dx, dy)
        elif cur_best == best_score:
            # deterministic tie-break: prefer moves that generally move away from opponent corner direction
            # (helps avoid getting stuck in mirror contests).
            # Compare by dot product with vector from opponent to self (favor increasing distance).
            vx, vy = sx - ox, sy - oy
            bx, by = best_move
            curd = (nx - ox) * vx + (ny - oy) * vy
            prevd = (sx + bx - ox) * vx + (sy + by - oy) * vy
            if curd > prevd:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a target resource that is close to us and relatively far from opponent
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Lower is better
            score = d_me * 2 - d_opp
            tie = (rx, ry)
            cand = (score, tie)
            if best is None or cand < best:
                best = cand
                target = (rx, ry)

    # Score candidate moves by progress to target + safety from opponent + resource pickup
    best_move = (0, 0)
    best_score = None
    tx, ty = target if target is not None else (sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)

        # If stepping onto a resource, strongly prefer it
        on_res = 1 if any((nx == rx and ny == ry) for rx, ry in resources) else 0

        # Prefer moves that increase opponent distance slightly while reducing distance to target
        score = (-d_to_t) + 0.15 * d_to_o + 5.0 * on_res

        cand = (score, -abs(dx), -abs(dy), nx, ny)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
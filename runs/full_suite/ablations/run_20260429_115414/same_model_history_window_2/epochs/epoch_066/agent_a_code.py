def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def opp_best_dist_for_target(tx, ty):
        best = 10**9
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < best:
                    best = d
        return best if best != 10**9 else cheb(ox, oy, tx, ty)

    if not resources:
        # deterministic fallback: move toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestd = 10**9
        bestlex = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd or (d == bestd and ((dx, dy) < bestlex if bestlex is not None else True)):
                    bestd = d
                    best = (dx, dy)
                    bestlex = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # choose the target that maximizes immediate advantage against opponent's next greedy step
        local_best = -10**18
        for tx, ty in resources:
            myd = cheb(nx, ny, tx, ty)
            oppd = opp_best_dist_for_target(tx, ty)
            # advantage: lower my distance and higher opponent distance
            score = (oppd - myd) * 100 - myd
            if score > local_best:
                local_best = score
        if local_best > best_score or (local_best == best_score and (dx, dy) < best_move):
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
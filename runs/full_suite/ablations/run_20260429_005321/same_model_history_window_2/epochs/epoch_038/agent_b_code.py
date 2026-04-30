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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_overall = None
        best_delta = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            best_for_move = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer: smaller myd; larger (opd - myd) i.e., harder for opponent
                # Lex tie-breaker includes coordinates for determinism.
                cand = (myd, -(opd - myd), rx, ry)
                if best_for_move is None or cand < best_for_move:
                    best_for_move = cand
            if best_for_move is not None and (best_overall is None or best_for_move < best_overall):
                best_overall = best_for_move
                best_delta = [dx, dy]
        return [int(best_delta[0]), int(best_delta[1])]
    else:
        # Fallback: head to the corner opposite the opponent
        if (ox + oy) <= (sx + sy):
            tx, ty = w - 1, h - 1
        else:
            tx, ty = 0, 0
        best = None
        ans = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = (cheb(nx, ny, tx, ty), nx, ny)
            if best is None or v < best:
                best = v
                ans = [dx, dy]
        return [int(ans[0]), int(ans[1])]
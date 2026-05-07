def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else int(sx))
    sy = 0 if sy < 0 else (h - 1 if sy >= h else int(sy))
    ox = 0 if ox < 0 else (w - 1 if ox >= w else int(ox))
    oy = 0 if oy < 0 else (h - 1 if oy >= h else int(oy))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(px, py):
        if not resources:
            return (w - 1 - px, h - 1 - py)
        # Prefer cells we can reach sooner than opponent.
        best = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            key = (opd - myd, -myd, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_target(sx, sy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        tx, ty = best_target(nx, ny)
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Extra preference for keeping same row/col if opponent is sweep-row-like (deterministic bias).
        rowcol_bias = 0
        if abs(oy - ny) <= abs(oy - sy):
            rowcol_bias += 1
        if abs(ox - nx) <= abs(ox - sx):
            rowcol_bias += 1
        score = (opd - myd, -myd, rowcol_bias, -abs(tx - nx) - abs(ty - ny), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
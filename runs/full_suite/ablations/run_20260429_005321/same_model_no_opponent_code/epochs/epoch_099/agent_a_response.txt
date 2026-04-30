def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best_res = None
        best_key = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            key = (myd - opd, myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_res = (rx, ry)
        tx, ty = best_res
        best_move = None
        best_score = None
        for dx, dy, nx, ny in legal:
            myd2 = md(nx, ny, tx, ty)
            opd2 = md(ox, oy, tx, ty)
            # tiny deterministic preference for progress and not getting worse for contest
            score = (myd2, (myd2 - myd2), opd2, -dx, -dy, dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources visible: move toward center while keeping away from obstacles
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    bestd = None
    for dx, dy, nx, ny in legal:
        d = md(nx, ny, cx, cy)
        key = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
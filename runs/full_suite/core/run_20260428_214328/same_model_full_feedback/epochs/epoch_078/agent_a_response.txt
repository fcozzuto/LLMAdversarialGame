def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax + ay

    def nearest_self(x, y):
        best = 10**9
        for rx, ry in resources:
            d = md(x, y, rx, ry)
            if d < best: best = d
        return best if resources else 10**9

    if not resources:
        tx, ty = (w - 1, 0) if sx + sy <= ox + oy else (0, h - 1)
        bestv = -10**18
        bestm = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = md(nx, ny, tx, ty) * -1 + md(nx, ny, ox, oy) * 0.2
            if v > bestv:
                bestv = v
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        self_near = 10**9
        best_margin = -10**9
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            if sd < self_near: self_near = sd
            od = md(ox, oy, rx, ry)
            margin = od - sd  # positive means we are closer than opponent
            if margin > best_margin: best_margin = margin

        opp_near = md(nx, ny, ox, oy)
        safe_bonus = 0.15 * opp_near  # avoid walking into opponent unless it helps margin
        score = (best_margin * 10.0) - (self_near * 1.0) + safe_bonus

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
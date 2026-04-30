def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            score = (myd - opd * 0.8, myd)  # smaller is better
            if best is None or score < best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
        best_step = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            cur = md(nx, ny, tx, ty)
            tie = (cur, dx, dy)
            if best_step is None or tie < best_step[0]:
                best_step = (tie, (dx, dy))
        if best_step is not None:
            return [best_step[1][0], best_step[1][1]]

    cx, cy = w // 2, h // 2
    best_step = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cur = md(nx, ny, cx, cy)
        tie = (cur, dx, dy)
        if best_step is None or tie < best_step[0]:
            best_step = (tie, (dx, dy))
    if best_step is not None:
        return [best_step[1][0], best_step[1][1]]

    return [0, 0]
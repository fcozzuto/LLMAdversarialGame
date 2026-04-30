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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def score_from_pos(px, py):
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return -(md(px, py, cx, cy))
        best_adv = None
        best_dist = None
        for rx, ry in resources:
            myd = md(px, py, rx, ry)
            opd = md(ox, oy, rx, ry)
            adv = myd - opd  # smaller is better (more ahead)
            if best_adv is None or adv < best_adv or (adv == best_adv and myd < best_dist):
                best_adv, best_dist = adv, myd
        # prioritize being earlier; also slightly prefer being closer overall for tie stability
        return -best_adv * 10 - best_dist

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = score_from_pos(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [int(dx), int(dy)]

    return best_move if best_move in ([-1, -1], [0, -1], [1, -1], [-1, 0], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]) else [0, 0]
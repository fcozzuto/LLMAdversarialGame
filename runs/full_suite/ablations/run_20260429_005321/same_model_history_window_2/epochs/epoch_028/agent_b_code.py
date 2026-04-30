def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    cur = (sx, sy)
    if resources:
        targets = resources
        best_dxdy = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            npos = (nx, ny)
            dmin = min(dist(npos, t) for t in targets)
            score = (dmin, abs(nx - ox) + abs(ny - oy))
            if best_score is None or score < best_score:
                best_score = score
                best_dxdy = (dx, dy)
        if best_dxdy is not None:
            return [best_dxdy[0], best_dxdy[1]]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    far_opp = (0 <= w - 1 and 0 <= h - 1)
    best_dxdy = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        npos = (nx, ny)
        d_to_center = abs(nx - cx) + abs(ny - cy)
        d_from_opp = abs(nx - ox) + abs(ny - oy)
        score = (-d_from_opp, d_to_center)  # maximize distance from opponent, then center
        if best_score is None or score < best_score:
            best_score = score
            best_dxdy = (dx, dy)
    if best_dxdy is not None:
        return [best_dxdy[0], best_dxdy[1]]
    return [0, 0]
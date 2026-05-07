def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if sd <= od:
            score = 10000 + (od - sd) * 20 - sd  # prioritize resources we can reach first/tie
        else:
            score = (od - sd) * 2 - sd + 3 * (od)  # avoid straight denial races; still seek longer-term wins
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = []
    primary = (dx, dy)
    moves.append(primary)
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                continue
            if (mx, my) != primary:
                moves.append((mx, my))
    moves.append((0, 0))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_m = (0, 0)
    best_md = None
    for mx, my in moves[:10]:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        md = cheb(nx, ny, tx, ty)
        if best_md is None or md < best_md:
            best_md = md
            best_m = (mx, my)

    return [int(best_m[0]), int(best_m[1])]
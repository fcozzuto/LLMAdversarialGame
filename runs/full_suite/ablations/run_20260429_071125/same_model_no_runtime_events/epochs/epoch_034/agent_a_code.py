def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        best_diff = -10**18
        for rx, ry in resources:
            ds = king_dist(sx, sy, rx, ry)
            do = king_dist(ox, oy, rx, ry)
            diff = do - ds
            if diff > best_diff:
                best_diff = diff
                best = (rx, ry)
        tx, ty = best
        cur_adv = king_dist(ox, oy, tx, ty) - king_dist(sx, sy, tx, ty)
    else:
        tx, ty = (w // 2, h // 2)
        cur_adv = king_dist(ox, oy, tx, ty) - king_dist(sx, sy, tx, ty)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = king_dist(nx, ny, tx, ty)
        opp_d = king_dist(ox, oy, tx, ty)
        score = (opp_d - self_d) * 1000 - (self_d)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    if best_score < -10**17 and valid(sx, sy):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
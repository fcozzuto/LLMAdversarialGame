def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # prefer resources that are closer to us and not closer to opponent; slight tie-break for nearer overall
        val = (sd - 1.1 * od, sd, rx, ry)
        if best is None or val < best[0]:
            best = (val, (rx, ry))
    tx, ty = best[1]

    desired = []
    sdx = 0 if tx == sx else (1 if tx > sx else -1)
    sdy = 0 if ty == sy else (1 if ty > sy else -1)
    desired.append((sdx, sdy))
    if sdx != 0:
        desired.append((sdx, 0))
    if sdy != 0:
        desired.append((0, sdy))

    # evaluate candidate moves: prefer moving to reduce distance to target while avoiding obstacles
    best_m = None
    best_score = None
    for dx, dy in desired + [m for m in moves if m not in desired]:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        score = (d, -(sdx * dx + sdy * dy), opp_d)
        if best_score is None or score < best_score:
            best_score = score
            best_m = (dx, dy)

    if best_m is None:
        # all blocked, stay
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]
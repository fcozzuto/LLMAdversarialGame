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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        target_x = ox
        target_y = oy
    else:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd <= opd:
                v = 200000 - myd * 300 - (opd - myd) * 50
            else:
                v = - (myd - opd) * 2000 - myd * 20
            if v > bestv:
                bestv = v
                best = (rx, ry)
        target_x, target_y = best[0], best[1]

    cur_sep = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            rx, ry = target_x, target_y
            myd2 = cheb(nx, ny, rx, ry)
            opd2 = cheb(ox, oy, rx, ry)
            if myd2 <= opd2:
                score = 200000 - myd2 * 300 - (opd2 - myd2) * 50
            else:
                score = - (myd2 - opd2) * 2000 - myd2 * 20
        else:
            score = -cheb(nx, ny, target_x, target_y)

        sep = cheb(nx, ny, ox, oy)
        score += (sep - cur_sep) * 5  # slight anti-collapse / denial bias

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]
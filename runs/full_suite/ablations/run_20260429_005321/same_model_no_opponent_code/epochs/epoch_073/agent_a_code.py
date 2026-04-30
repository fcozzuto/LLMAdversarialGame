def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if resources:
            myd_best = 10**9
            oppd_best = 10**9
            for rx, ry in resources:
                myd = dist(nx, ny, rx, ry)
                oppd = dist(ox, oy, rx, ry)
                if myd < myd_best:
                    myd_best = myd
                    oppd_best = oppd
                elif myd == myd_best and oppd < oppd_best:
                    oppd_best = oppd
            sc = (oppd_best - myd_best) * 3 - myd_best
            if oppd_best - myd_best >= 2:
                sc += 8
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            myd = abs(nx - cx) + abs(ny - cy)
            sc = -myd
        # Slightly avoid letting opponent gain distance advantage
        cur_my = dist(sx, sy, ox, oy)
        nxt_my = dist(nx, ny, ox, oy)
        sc += (cur_my - nxt_my) * 0.1
        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best
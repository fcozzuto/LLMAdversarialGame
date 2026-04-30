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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    candidates = []
    if ok(sx, sy):
        candidates = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not candidates:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best_mv = None
        best_sc = -10**9
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            d_to_opp = cheb(nx, ny, ox, oy)
            d_to_edge = cheb(nx, ny, w - 1 - sx, h - 1 - sy)
            sc = d_to_opp + 0.01 * d_to_edge
            if sc > best_sc:
                best_sc = sc
                best_mv = (dx, dy)
        return [int(best_mv[0]), int(best_mv[1])]

    best_mv = None
    best_sc = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        my_best_gain = -10**9
        my_dist = 10**9
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            gain = d_op - d_my  # positive means we're closer now than opponent
            if gain > my_best_gain:
                my_best_gain = gain
                my_dist = d_my
            elif gain == my_best_gain and d_my < my_dist:
                my_dist = d_my
        # Prefer winning a race (gain), then being closer, then slightly away from opponent
        d_opp_now = cheb(nx, ny, ox, oy)
        sc = 1000 * my_best_gain - my_dist + 0.05 * d_opp_now
        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = r[0], r[1]
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target(px, py):
        # pick resource that favors us: smallest (ds - do), then smallest ds
        best = None
        best_key = None
        for tx, ty in resources:
            ds = cheb(px, py, tx, ty)
            do = cheb(ox, oy, tx, ty)
            key = (ds - do, ds, cheb(sx, sy, tx, ty))
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        return best

    target = best_target(sx, sy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    tx, ty = target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate move by contest advantage to nearest resource(s)
        self_min = 10**9
        opp_min = 10**9
        self_second = 10**9
        opp_second = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < self_min:
                self_second, self_min = self_min, ds
            elif ds < self_second:
                self_second = ds
            if do < opp_min:
                opp_second, opp_min = opp_min, do
            elif do < opp_second:
                opp_second = do

        # Also include progress toward a locally best target (to avoid oscillations)
        prog = cheb(nx, ny, tx, ty)
        prog0 = cheb(sx, sy, tx, ty)
        toward = 0 if prog0 == 0 else (prog0 - prog)

        key = (self_min - opp_min, self_min, -toward, self_second - opp_second, dx*0 + dy*0)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
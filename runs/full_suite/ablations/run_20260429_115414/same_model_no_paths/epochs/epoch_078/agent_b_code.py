def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (-10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            sc = -d
            if sc > best[0]:
                best = (sc, (dx, dy))
        return [best[1][0], best[1][1]]

    best_move = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Prefer: move that creates the best immediate "arrival advantage" on some resource.
        # Score = (opp_dist - self_dist) - 0.15*min(self_dist), so advantage dominates.
        # Also mildly avoid giving opponent a closer jump to that same chosen resource.
        local_best = -10**18
        for tx, ty in resources:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            slack = od - sd  # positive means we are closer than opponent
            self_after = sd
            opp_after = cheb(ox, oy, tx, ty)
            sc = slack * 10 - 0.15 * self_after - 0.05 * opp_after
            if sc > local_best:
                local_best = sc

        # If no move yields positive slack, prefer minimizing our distance to the resource
        # that is currently best (closest-to-us under our control).
        if local_best < 0:
            my_min = 10**9
            for tx, ty in resources:
                d = cheb(nx, ny, tx, ty)
                if d < my_min: my_min = d
            local_best = -my_min

        if local_best > best_sc:
            best_sc = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
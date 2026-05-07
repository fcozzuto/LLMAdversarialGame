def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy
    def neigh_legal(x, y):
        c = 0
        for ddx, ddy in moves:
            nx, ny = x + ddx, y + ddy
            if legal(nx, ny):
                c += 1
        return c

    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best, bestv = (0, 0), -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = -cheb(nx, ny, cx, cy) + 0.25 * neigh_legal(nx, ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best, bestv = (0, 0), -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Evaluate "threat": if opponent is closer to some resource, discourage.
        min_me = 10**9
        min_op = 10**9
        reach_me_on = False
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            if dme < min_me: min_me = dme
            if dop < min_op: min_op = dop
            if dme == 0:
                reach_me_on = True

        # If we can grab a resource now, strongly prefer.
        v = 0.0
        if reach_me_on:
            v += 1000.0
        # Prefer reducing distance to the best reachable resource.
        v += -2.2 * min_me
        # If opponent is closer to the nearest resource, penalize (give up contested targets).
        v += -1.0 * max(0, (min_op - min_me))
        # Small preference for staying mobile.
        v += 0.15 * neigh_legal(nx, ny)

        if v > bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        best, bestv = (0, 0), -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose a target resource, preferring ones we can reach not later than opponent.
    cur = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # prioritize: (1) reachable advantage, (2) proximity, (3) stability tie-break by coords
        cur.append(((do - ds), -ds, rx, ry))
    cur.sort(reverse=True)
    _, nds, tr_x, tr_y = cur[0]
    target = (tr_x, tr_y)

    best, bestv = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ds_new = cheb(nx, ny, target[0], target[1])
        do_new = cheb(ox, oy, target[0], target[1])
        # If we step onto a resource, strongly prefer it.
        on = 1 if (nx, ny) in resources else 0
        v = (on * 10**6) + (-ds_new * 10) + (do_new * 3)
        # Small tie-break: also try to increase distance from opponent in general.
        v += cheb(nx, ny, ox, oy) * 0.1
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv, best = v, (dx, dy)

    return [int(best[0]), int(best[1])]
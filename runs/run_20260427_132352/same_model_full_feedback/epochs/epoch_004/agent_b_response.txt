def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -cheb(nx, ny, cx, cy) - 0.05 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    res_set = set(tuple(p) for p in resources)
    best = (0, 0)
    bestv = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Collecting this cell
        v = 0
        if (nx, ny) in res_set:
            v += 10**7

        # Advantage on resources: we want opponent far and us close to same remaining resources
        ds = 10**9
        do = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d1 = cheb(nx, ny, rx, ry)
            if d1 < ds: ds = d1
            d2 = cheb(ox, oy, rx, ry)
            if d2 < do: do = d2

        v += (do - ds) * 1000.0

        # Secondary tie-breakers: move toward nearest resource; keep some distance from opponent
        v += -ds * 2.0
        v += 0.15 * cheb(nx, ny, ox, oy)

        if v > bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]
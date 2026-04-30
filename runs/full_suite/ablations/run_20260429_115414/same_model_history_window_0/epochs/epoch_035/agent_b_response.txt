def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    resources = observation.get('resources', [])
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    if not resources:
        dxs = [-1, 0, 1]
        best = None
        bestv = -10**9
        for dx in dxs:
            for dy in dxs:
                nx, ny = sx + dx, sy + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h: continue
                if (nx, ny) in obstacles: continue
                v = cheb(nx, ny, ox, oy)
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best if best is not None else [0, 0]
    best_r = None
    best_val = -10**18
    best_md = 10**9
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - md) * 10 - md
        if val > best_val or (val == best_val and md < best_md):
            best_val = val
            best_md = md
            best_r = (rx, ry)
    rx, ry = best_r
    dirs = [-1, 0, 1]
    best = [0, 0]
    best_cost = 10**18
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(nx, ny, ox, oy)
            cost = myd * 3 - cheb(ox, oy, rx, ry) * 1.5 + 0.15 * (1 if opd == 0 else 1 / (opd + 1))
            if cost < best_cost:
                best_cost = cost
                best = [dx, dy]
    return [int(best[0]), int(best[1])]
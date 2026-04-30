def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        if not inb(x, y): return 10**9
        if (x, y) in obstacles: return 10**8
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                if (x + dx, y + dy) in obstacles: p += 2
        return p

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            p = obs_pen(nx, ny)
            if p >= 10**8: 
                continue
            v = -(p) - 0.02 * (abs(nx - tx) + abs(ny - ty))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best_target = None
    best_gain = -10**18
    best_my_dist = 10**18
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gain = od - md
        if gain > best_gain or (gain == best_gain and md < best_my_dist):
            best_gain, best_my_dist = gain, md
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        p = obs_pen(nx, ny)
        if p >= 10**8:
            continue
        dself = cheb(nx, ny, tx, ty)
        dopp = cheb(nx, ny, ox, oy)
        v = 1000 * (-dself) - 5 * p + 0.01 * dopp
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val, best_move = v, (dx, dy)
    return [best_move[0], best_move[1]]
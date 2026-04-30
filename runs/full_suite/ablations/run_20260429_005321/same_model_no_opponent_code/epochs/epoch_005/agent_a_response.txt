def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obst = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obst

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in obst:
                    c += 1
        return c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            v = adj_obst(nx, ny) * -3 - cheb(nx, ny, ox, oy) * 0.1
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    my_d0 = cheb(sx, sy, ox, oy)
    best_target = None
    best_adv = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = (opd - myd) * 100 - myd
        # Prefer not-too-far resources to keep pressure
        adv -= 2 * (myd > (my_d0 + 3))
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)
    tr, ty = best_target
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        myd = cheb(nx, ny, tr, ty)
        opd = cheb(ox, oy, tr, ty)
        step_improve = (cheb(sx, sy, tr, ty) - myd)
        collect = 1 if (nx, ny) in set((p[0], p[1]) for p in resources) else 0
        v = step_improve * 20 + (opd - myd) * 10 + collect * 200
        # Avoid moving into tighter obstacle configurations
        v -= adj_obst(nx, ny) * 6
        # If we can't secure advantage, increase distance from opponent
        v += cheb(nx, ny, ox, oy) * 0.05
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]
    return best
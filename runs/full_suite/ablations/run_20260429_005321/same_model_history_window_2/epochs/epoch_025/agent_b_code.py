def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = moves

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in obst:
                pen += 1
        return pen

    best = None
    best_val = -10**18

    if resources:
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not valid(nx, ny):
                nx, ny = sx, sy
            pen = obst_adj_pen(nx, ny)
            v = -0.6 * (abs(nx - sx) + abs(ny - sy)) - 0.12 * pen
            # choose resource that maximizes (opponent_reach_advantage)
            local = -10**18
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # want resources where we are closer than opponent (od - sd large)
                cand = (od - sd) - 0.25 * sd
                if cand > local:
                    local = cand
            v += local
            if v > best_val:
                best_val = v
                best = (dxm, dym)
    else:
        # no visible resources: drift to safer/away from opponent while keeping options open
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not valid(nx, ny):
                nx, ny = sx, sy
            pen = obst_adj_pen(nx, ny)
            myd = cheb(nx, ny, ox, oy)
            cent = cheb(nx, ny, int(cx), int(cy))
            v = 0.9 * myd - 0.03 * cent - 0.2 * pen
            if v > best_val:
                best_val = v
                best = (dxm, dym)

    return [int(best[0]), int(best[1])]
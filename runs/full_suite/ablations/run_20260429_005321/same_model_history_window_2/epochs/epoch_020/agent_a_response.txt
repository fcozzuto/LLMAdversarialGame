def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    neigh_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh_dirs:
            if (x + dx, y + dy) in obst:
                pen += 1
        return pen

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Deterministic tie-breaking order: fixed moves list above.

    if not resources:
        best_sc = -10**9
        best = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            d_opp = cheb(nx, ny, ox, oy)
            sc = d_opp - 1.5 * obst_adj_pen(nx, ny)
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return best

    best_sc = -10**9
    best = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d_opp = cheb(nx, ny, ox, oy)

        # nearest resource distance
        mind = 10**9
        target = resources[0]
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < mind:
                mind = d
                target = (rx, ry)

        # progress bias: reduce distance from current to that chosen target
        d_cur = cheb(sx, sy, target[0], target[1])
        d_next = mind
        progress = d_cur - d_next  # positive if closer

        # Also lightly prefer moving toward higher "resource value" proxies: closeness to farthest resource
        farthest = 0
        for rx, ry in resources:
            df = cheb(sx, sy, rx, ry)
            if df > farthest:
                farthest = df

        sc = (-mind) + 0.35 * d_opp + 0.6 * progress - 1.2 * obst_adj_pen(nx, ny) + 0.02 * (farthest - d_next)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best
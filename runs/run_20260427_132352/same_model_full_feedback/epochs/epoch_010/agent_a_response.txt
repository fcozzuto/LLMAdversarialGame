def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not inb(sx, sy): return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = w // 2, h // 2
        best, bestv = None, None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst: 
                continue
            v = (-(cheb(nx, ny, cx, cy)), -cheb(nx, ny, ox, oy), -cheb(nx, ny, sx, sy))
            if bestv is None or v > bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]

    target_mid_x = (sx + ox) // 2
    target_mid_y = (sy + oy) // 2

    # Choose move by evaluating next position's ability to secure resources over the opponent.
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Find best resource by self-opponent race advantage from (nx,ny).
        local_best = None
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Primary: race advantage; Secondary: prefer closer own; Tertiary: avoid opponent-favored resources.
            v = (do - ds, -ds, do, -cheb(nx, ny, target_mid_x, target_mid_y))
            if local_best is None or v > local_best:
                local_best = v
        # Add a small incentive to reduce distance to midline when races tie.
        if local_best is None:
            v2 = (-cheb(nx, ny, target_mid_x, target_mid_y),)
        else:
            v2 = (local_best[0], local_best[1], local_best[2], local_best[3], -cheb(nx, ny, sx, sy))
        if best_val is None or v2 > best_val:
            best_val = v2
            best_move = [dx, dy]

    return best_move
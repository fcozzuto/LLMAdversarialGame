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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # fallback: move away from opponent if possible, else deterministic safe move
        best = None
        best_sc = -10**18
        for dx, dy in neigh:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
                continue
            sc = cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc, best = sc, (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    tx, ty = resources[0]
    bd = cheb(sx, sy, tx, ty)
    for rx, ry in resources[1:]:
        d = cheb(sx, sy, rx, ry)
        if d < bd:
            bd, tx, ty = d, rx, ry

    best = None
    best_sc = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        dist = cheb(nx, ny, tx, ty)
        sc = -dist
        # slight tie-break to avoid staying in place when equally good
        if dx == 0 and dy == 0:
            sc -= 0.01
        if sc > best_sc:
            best_sc, best = sc, (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def obst_adj(x, y):
        c = 0
        for ax in (-1, 0, 1):
            nx = x + ax
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                ny = y + ay
                if (nx, ny) in obstacles:
                    c += 1
        return c

    # If no resources visible, head to center-ish to avoid deadlocks.
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    bestv = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; avoid obstacle-adjacent cells.
        adj = obst_adj(rx, ry)
        v = (-(ds) * 3) + (-(do) * 1) + (-(adj) * 4) + (2 if adj == 0 else 0)
        if best is None or v > bestv:
            bestv = v
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order: already fixed order above.
    bestm = (0, 0)
    bestmv = -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Avoid moving near obstacles unless necessary.
        step_adj = obst_adj(nx, ny)
        dself = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)
        v = (-(dself) * 5) + (-(step_adj) * 3) + (-(dop) * 0.2)
        # Small preference to progress in general direction to target.
        v += 0.1 * (mx * (1 if tx > sx else (-1 if tx < sx else 0)) + my * (1 if ty > sy else (-1 if ty < sy else 0)))
        if v > bestmv:
            bestmv = v
            bestm = (mx, my)

    return [int(bestm[0]), int(bestm[1])]
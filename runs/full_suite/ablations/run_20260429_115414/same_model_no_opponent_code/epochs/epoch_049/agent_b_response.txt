def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        target = (tx, ty)
    else:
        best = resources[0]
        bestv = -10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            v = (do - ds) * 100 - ds * 3 - cheb(rx, ry, (w - 1) // 2, (h - 1) // 2)
            if v > bestv or (v == bestv and (rx, ry) < best):
                bestv = v
                best = (rx, ry)
        target = best

    tx, ty = target
    cur_ds = cheb(sx, sy, tx, ty)
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            v = (do - nds) * 100 - nds * 4
            # Slightly prefer forward progress; discourage stepping away
            if nds <= cur_ds:
                v += 5
            cand.append((v, -nds, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][2]), int(cand[0][3])]
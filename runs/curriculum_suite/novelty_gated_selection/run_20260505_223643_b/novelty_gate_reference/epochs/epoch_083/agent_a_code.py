def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a target resource we can contest; then step greedily toward it with obstacle-aware checks.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Advantage: prioritize cells we reach no later than opponent; break ties by shorter distance.
        adv = 0 if ds <= do else 1
        # Small preference for resources closer to our "front" from our corner.
        front = rx + ry if sx + sy <= (w - 1) + (h - 1) - (sx + sy) else (w - 1 - rx) + (h - 1 - ry)
        # Sweep-row archetype tends to take lines; lightly prefer resources not aligned with opponent in row/col.
        align = 0
        if ry == oy or rx == ox:
            align = 1
        cand = (adv, align, ds, -front, rx, ry)
        if best is None or cand < best[0]:
            best = (cand, (rx, ry))

    tx, ty = best[1]

    # Evaluate immediate moves (including staying) toward target, with obstacle avoidance.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Discourage moves that would reduce contest advantage when close.
        nds = d
        ndo = cheb(ox, oy, tx, ty)
        adv_after = 0 if nds <= ndo else 1
        candm = (adv_after, d, 0 if (nx, ny) == (tx, ty) else 1, abs(nx - ox) + abs(ny - oy))
        if bestm is None or candm < bestm[0]:
            bestm = (candm, [dx, dy])

    return bestm[1] if bestm is not None else [0, 0]
def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive: we can arrive earlier
        val = 1000 * margin - (ds * 3) - (do * 0.5)
        # Prefer closer resources when tie, and slightly prefer those far from opponent
        val += (do - ds) * 0.1
        if best is None or val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    curd = cheb(sx, sy, tx, ty)
    bestm = (0, 0)
    bestmd = 10**9
    bestaux = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # primary: reduce distance; secondary: increase margin of advantage at next step
        if nd < bestmd or (nd == bestmd and (do - nd) > bestaux):
            bestmd = nd
            bestm = (dx, dy)
            # recompute do' as opponent distance to target from its current position (static step)
            bestaux = (cheb(ox, oy, tx, ty) - nd)

    # If any move keeps us from getting closer, choose one that maximizes distance margin
    if bestmd >= curd:
        bestm2 = (0, 0)
        bestmargin = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            nd = cheb(nx, ny, tx, ty)
            margin = cheb(ox, oy, tx, ty) - nd
            if margin > bestmargin:
                bestmargin = margin
                bestm2 = (dx, dy)
        bestm = bestm2

    return [int(bestm[0]), int(bestm[1])]
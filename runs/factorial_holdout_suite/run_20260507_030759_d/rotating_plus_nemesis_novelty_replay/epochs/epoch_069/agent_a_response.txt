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

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best = None
    bestv = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        takeover = do - ds  # >0 means we can reach no later than opponent
        # prioritize beating opponent; then shorter distance; deterministic parity tie-break
        v = takeover * 1000 - ds * 3 - ((rx * 17 + ry * 31) & 7)
        if v > bestv:
            bestv = v
            best = (rx, ry, ds, do)

    rx, ry, ds, do = best
    # If we can't beat any resource, pick the least-losing race; also drift toward opponent-relevant area.
    if do - ds <= 0:
        # try to reduce lead over opponent by moving to a position that minimizes (self_dist - op_dist) to the chosen target
        pass

    curx, cury = sx, sy
    bestm = (0, 0)
    bestd = 10**9
    besttie = 10**9
    for dx, dy in moves:
        nx, ny = curx + dx, cury + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, rx, ry)
        tie = (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))
        if d < bestd or (d == bestd and tie < besttie):
            bestd = d
            besttie = tie
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]
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

    best_res = None
    best_score = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        takeover = (do - ds)  # positive means we can reach no later than opponent
        score = takeover * 20 - ds  # strongly prefer takeovers
        # small bias to avoid dithering when tie: prefer resources closer to our current heading toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= 0.01 * (cheb(rx, ry, int(cx), int(cy)))
        if score > best_score:
            best_score = score
            best_res = (rx, ry)

    rx, ry = best_res
    # If we can't beat opponent on any resource, recompute target as nearest resource to us
    if best_score < 0:
        rx, ry = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = cheb(nx, ny, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # local utility: prioritize reducing our distance and preserving takeover margin
        util = (d_opp - d_self) * 20 - d_self
        cand.append((util, -abs(nx - rx) - abs(ny - ry), dx, dy))
    cand.sort(reverse=True)
    if not cand:
        return [0, 0]
    return [int(cand[0][2]), int(cand[0][3])]
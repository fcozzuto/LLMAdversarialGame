def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose target where we are most likely to arrive first (diagonal moves => Chebyshev)
    best_t = None
    best_r = None
    for rx, ry in resources:
        st = cheb(sx, sy, rx, ry)
        ot = cheb(ox, oy, rx, ry)
        # Strong preference for positive advantage; tie-break toward nearer target to secure collection
        adv = ot - st
        tieb = -st - 0.001 * (cheb(ox, oy, sx, sy))
        key = (adv, tieb)
        if best_t is None or key > best_t:
            best_t, best_r = key, (rx, ry)

    rx, ry = best_r
    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_mk = None
    best = (0, 0)

    # Local step selection: maximize our improvement in "first arrival margin"
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        st2 = cheb(nx, ny, rx, ry)
        ot = cheb(ox, oy, rx, ry)
        margin = ot - st2
        # Small bias to keep moving toward the target, and avoid stepping closer to opponent only when it doesn't help margin
        closeness = cheb(nx, ny, rx, ry)
        opp_close = cheb(nx, ny, ox, oy)
        mk = (margin, -closeness, opp_close, -dx * dy)
        if best_mk is None or mk > best_mk:
            best_mk, best = mk, (dx, dy)

    return [int(best[0]), int(best[1])]
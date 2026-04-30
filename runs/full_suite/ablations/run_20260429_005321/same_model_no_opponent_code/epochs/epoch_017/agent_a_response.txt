def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a target resource where we have the biggest "closeness margin" over opponent.
    best_r = None
    best_margin = -10**18
    if resources:
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd
            if margin > best_margin or (margin == best_margin and (sd < cheb(ox, oy, rx, ry))):
                best_margin = margin
                best_r = (rx, ry)
        if best_r is None:
            best_r = resources[0]
    else:
        # No visible resources: drift toward center while keeping distance from opponent.
        best_r = (w // 2, h // 2)

    tx, ty = best_r
    best_move = (0, 0)
    best_score = -10**18
    best_sd = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nd_self = cheb(nx, ny, tx, ty)
        nd_opp = cheb(ox, oy, tx, ty)
        # Primary: maximize ability to be first (increase opponent distance relative to us).
        # Secondary: reduce our distance to the target.
        # Tertiary: avoid moving closer to opponent (encourage safer routes).
        opp_dist_now = cheb(nx, ny, ox, oy)
        opp_dist_cur = cheb(sx, sy, ox, oy)
        score = (nd_opp - nd_self) * 1000 - nd_self * 3 + (opp_dist_now - opp_dist_cur) * 2
        if score > best_score or (score == best_score and nd_self < best_sd):
            best_score = score
            best_sd = nd_self
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
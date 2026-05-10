def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in self_role) or (self_role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If evader, steer toward farthest available corner; if pursuer, chase minimizing distance.
    target_corner = None
    if not pursuer:
        bestc = None
        bestd = None
        for cx, cy in corners:
            if (cx, cy) in blocked:
                continue
            d = cheb(sx, sy, cx, cy)
            # Prefer corners that are far from pursuer (and also reachable by not being same as pursuer)
            dd = cheb(cx, cy, ox, oy)
            score = (dd, -d)
            if bestd is None or score > bestd:
                bestd = score
                bestc = (cx, cy)
        target_corner = bestc if bestc is not None else corners[0]

    best_move = [0, 0]
    best_val = None

    # Deterministic tie-break: earliest in moves order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        if pursuer:
            d = cheb(nx, ny, ox, oy)
            # Capture prioritized implicitly by d==0
            val = (-10 if d == 0 else 0, -d, -dx, -dy)
        else:
            tcx, tcy = target_corner
            # Maximize distance from pursuer, also align with target corner
            dfo = cheb(nx, ny, ox, oy)
            dt = cheb(nx, ny, tcx, tcy)
            val = (dfo, -dt, -dx, -dy)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move
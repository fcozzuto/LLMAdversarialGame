def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # If stuck, try any free neighboring move.
    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick a target deterministically: resource we can reach no slower than opponent; else closest by us.
    target = None
    if resources:
        best = None
        for (rx, ry) in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; tie-break by position and resource "density" proxy.
            score = (do - ds, -ds, -(rx + ry), rx, ry)
            if best is None or score > best:
                best = score
                target = (rx, ry)

    # Obstacle-aware local decision: choose move that minimizes our distance to target,
    # while also not giving the opponent a closer approach.
    if target is None:
        # No resources visible: move toward center to improve future access.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            score = (-cheb(nx, ny, cx, cy), -(abs(nx - cx) + abs(ny - cy)))
            if best is None or score > best:
                best = score
                best_move = [dx, dy]
        return best_move if best is not None else [0, 0]

    rx, ry = target
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        my_d = cheb(nx, ny, rx, ry)
        opp_d_after = cheb(ox, oy, rx, ry)  # opponent position unchanged this turn for our choice
        # Primary: get closer to target; Secondary: prevent being behind opponent;
        # Tertiary: avoid wandering to far edges.
        score = (-my_d, (opp_d_after - my_d), -(nx + ny), dx, dy)
        if best is None or score > best:
            best = score
            best_move = [dx, dy]
    return best_move
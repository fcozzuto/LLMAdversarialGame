def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Favor resources where we're not behind; penalize those the opponent is closer to.
            val = md - (od * 0.55)
            if best is None or val < best[0] or (val == best[0] and md < best[1]):
                best = (val, md, rx, ry)
        _, _, tx, ty = best

        candidates = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                d = cheb(nx, ny, tx, ty)
                candidates.append((d, cheb(nx, ny, ox, oy), dx, dy))
        if not candidates:
            return [0, 0]
        candidates.sort(key=lambda t: (t[0], -t[1], t[2], t[3]))
        return [int(candidates[0][2]), int(candidates[0][3])]

    # No visible resources: move toward the corner that is farther from opponent (denial).
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx, sy + dy
    if ok(nx, ny):
        return [int(dx), int(dy)]
    # Fallback: any valid move that reduces distance to the chosen corner.
    best = (10**9, 10**9, 0, 0)
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if ok(nx, ny):
            d = cheb(nx, ny, tx, ty)
            od = cheb(nx, ny, ox, oy)
            cand = (d, -od, ddx, ddy)
            if cand < best:
                best = cand
    return [int(best[2]), int(best[3])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = corners[0]
    best = 10**9
    for cx, cy in corners:
        d = cheb(ox, oy, cx, cy)
        if d < best:
            best = d
            tx, ty = cx, cy

    # "Cutoff" point: keep position one step closer to the opponent's nearest-corner direction.
    dx1 = 0 if tx == ox else (1 if tx > ox else -1)
    dy1 = 0 if ty == oy else (1 if ty > oy else -1)
    cutoffx, cutoffy = ox + dx1, oy + dy1
    if not inb(cutoffx, cutoffy) or (cutoffx, cutoffy) in obs:
        cutoffx, cutoffy = tx, ty
        if (cutoffx, cutoffy) in obs:
            cutoffx, cutoffy = ox, oy

    # Choose move that best reduces distance to cutoff while not getting blocked by obstacles.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestv = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Primary: minimize distance to cutoff.
        v1 = cheb(nx, ny, cutoffx, cutoffy)
        # Secondary: minimize distance to opponent (to help pursuit).
        v2 = cheb(nx, ny, ox, oy)
        # Tiebreak: prefer moves that tighten opponent to the corner (maximize progress).
        oppprog = cheb(ox, oy, tx, ty) - cheb(ox, oy, tx, ty)  # deterministic 0, keep structure
        v = v1 * 100 + v2 * 2 + (0 if bestm is None else 0) + oppprog
        if v < bestv:
            bestv = v
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]
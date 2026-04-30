def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            score = cheb(nx, ny, cx, cy)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach strictly sooner; else prefer those still relatively close.
        # Tie-break: maximize (d_op - d_me), then minimize d_me.
        key = (0 if d_me < d_op else 1, -((d_op - d_me)), d_me, rx + ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    # Choose local move that minimizes distance to target with strong safety vs opponent proximity.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Also discourage stepping into cells that are very close to opponent if we can't secure target quickly.
        # Deterministic tie-breakers included.
        if cheb(sx, sy, tx, ty) < cheb(ox, oy, tx, ty):
            risk = 0
        else:
            risk = -d_opp
        score = (d_to, risk, -(nx - ox if nx != ox else ny - oy), nx, ny)
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]] if best else [0, 0]
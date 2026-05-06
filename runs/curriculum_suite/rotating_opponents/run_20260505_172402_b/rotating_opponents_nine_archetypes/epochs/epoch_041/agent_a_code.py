def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    tx, ty = None, None
    if res:
        best = None
        for x, y in res:
            d_me = cheb(sx, sy, x, y)
            d_op = cheb(ox, oy, x, y)
            # If opponent is closer/equal, penalize; else prefer nearby.
            score = d_me - 0.85 * d_op
            if best is None or (score, d_me) < best:
                best = (score, d_me, x, y)
        tx, ty = best[2], best[3]
    else:
        # No visible resources: steer toward opponent's opposite corner to open space.
        tx, ty = (w - 1) if ox < (w - 1) / 2 else 0, (h - 1) if oy < (h - 1) / 2 else 0

    dx0, dy0 = sign(tx - sx), sign(ty - sy)
    candidates = [
        (dx0, dy0),
        (dx0, 0),
        (0, dy0),
        (dx0, -dy0),
        (-dx0, dy0),
        (0, 0),
    ]
    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = cheb(nx, ny, tx, ty)
        # avoid stepping into "opponent reach" when it doesn't help us
        v2 = cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)
        score = (v, -v2)
        if best_val is None or score < best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    best = None
    best_d = 10**9
    for r in resources:
        rx, ry = r
        d = man(sx, sy, rx, ry)
        if d < best_d or (d == best_d and (rx, ry) < (best[0], best[1]) if best else True):
            best_d = d
            best = (rx, ry)

    tx, ty = best
    od = man(ox, oy, tx, ty)
    # If opponent is significantly closer, pick a different resource (closest to us among those not too contested).
    if od + 1 < best_d:
        best2 = best
        best2_d = best_d
        for r in resources:
            rx, ry = r
            myd = man(sx, sy, rx, ry)
            oppd = man(ox, oy, rx, ry)
            score = (myd, oppd - myd, (rx, ry))
            if (myd < best2_d and oppd - myd >= 0) or (best2 is best and oppd - myd >= 0 and myd < best2_d):
                best2 = (rx, ry)
                best2_d = myd
        tx, ty = best2

    moves = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist_to = man(nx, ny, tx, ty)
        dist_opp = man(nx, ny, ox, oy)
        val = -dist_to * 10 + dist_opp
        # small deterministic tie-breaker favor staying close to resources chosen
        val += -man(sx, sy, tx, ty) * 0.001
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move in ([0, -1], [0, 1], [-1, 0], [1, 0], [0, 0]) else [0, 0]
def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose target with a new rule: prefer resources where opponent is already closer,
    # but also bias toward reachable ones to avoid aimless interception.
    best = None
    best_key = None
    for cx, cy in resources:
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        # key: (how much closer opp is), then (prefer smaller our distance), then determinism
        key = (od - sd, -sd, -cx - 100 * cy)
        if best_key is None or key > best_key:
            best_key = key
            best = (cx, cy)

    tx, ty = best
    # If we are not competitive on that target, switch to our closest resource.
    sd0 = cheb(sx, sy, tx, ty)
    od0 = cheb(ox, oy, tx, ty)
    if od0 <= sd0:
        best2, best2_key = None, None
        for cx, cy in resources:
            sd = cheb(sx, sy, cx, cy)
            key = (-sd, -cx - 100 * cy)
            if best2_key is None or key > best2_key:
                best2_key = key
                best2 = (cx, cy)
        tx, ty = best2

    # Greedy one-step with obstacle-aware scoring + slight opponent pressure.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm, bestms = None, None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        d_opp_t = cheb(ox, oy, tx, ty)
        # Score: go to target; if opponent is closer, try to reduce our remaining distance and keep proximity.
        competitive = 1 if d_opp_t - sd0 > 0 else 0
        score = -d_to_t + (0.15 * d_to_o) + (0.35 * competitive * (sd0 - d_to_t))
        if bestms is None or score > bestms:
            bestms = score
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]
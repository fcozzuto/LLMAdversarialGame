def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # If standing on a resource, stay to collect.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # If no resources: maximize distance from opponent while improving toward center.
    if not resources:
        cx = (w - 1) / 2.0; cy = (h - 1) / 2.0
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            score = (cheb(nx, ny, ox, oy) * 5.0) - (cheb(nx, ny, cx, cy) * 1.0)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Choose a target resource deterministically: prioritize where opponent is closer, i.e., we must contest/block.
    best_t = resources[0]; best_cont = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry); opd = cheb(ox, oy, rx, ry)
        cont = (opd - myd)  # positive means opponent farther; negative means opponent closer (we should contest)
        # Convert to "need" score: more negative cont => higher need to contest.
        need = (-cont * 2.0) + (opd * 0.05)
        if need > best_cont:
            best_cont = need; best_t = (rx, ry)
    tx, ty = best_t

    # One-step evaluation: move that best improves distance-to-target while keeping distance from opponent and avoiding crowding.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if nx == tx and ny == ty:
            return [dx, dy]

        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)

        # Opponent "pressure": if opponent is closer to target than us, we try to reduce our gap fast.
        gap = (opd2 - myd2)  # bigger => opponent farther (good for us)

        # Keep away from opponent to reduce direct steals.
        dist_op = cheb(nx, ny, ox, oy)

        # Local mobility around next position (prefer less trapped).
        mob = 0
        for ddx, ddy in deltas:
            tx2, ty2 = nx + ddx, ny + ddy
            if valid(tx2, ty2):
                mob += 1

        score = (gap * 3.0) + (dist_op * 0.7) + (mob * 0.15) - (myd2 * 0.8)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]
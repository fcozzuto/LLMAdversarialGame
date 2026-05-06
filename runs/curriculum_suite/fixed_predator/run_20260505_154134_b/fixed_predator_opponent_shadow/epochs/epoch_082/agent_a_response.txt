def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Prioritize resources where we can arrive no later than opponent; fallback to our closest.
    def pick_resource_for_us():
        best = None
        best_key = None
        for cx, cy in resources:
            sd = cheb(sx, sy, cx, cy)
            od = cheb(ox, oy, cx, cy)
            # Prefer cells where we are closer (or can tie), then earlier arrival, then farther from corner to reduce chase mirror.
            key = (0 if sd <= od else 1, sd, -cx, -cy, -od)
            if best_key is None or key < best_key:
                best_key = key
                best = (cx, cy)
        return best

    target = pick_resource_for_us()
    tx, ty = target

    # Also consider an "intercept" resource: the one opponent is closest to.
    itx, ity = min(resources, key=lambda c: cheb(ox, oy, c[0], c[1]))
    # Small nudge: if we can reach opponent's closest resource earlier or tie, do it.
    intercept_mode = cheb(sx, sy, itx, ity) <= cheb(ox, oy, itx, ity)

    if intercept_mode:
        tx, ty = itx, ity

    # Candidate moves: pick the move that maximizes (coverage) and minimizes contest disadvantage.
    best_move = [0, 0]
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            # immediate reward if landing on a resource
            on_res = 1 if (nx, ny) in set(map(tuple, resources)) else 0
            d_us = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # contest: prefer moves where we are not worse than opponent after the move
            contest = 0 if d_us <= d_opp else 1
            # diversity-ish: steer away from opponent while progressing
            opp_dist = cheb(nx, ny, ox, oy)
            key = (0 if on_res else 1, contest, d_us, -opp_dist, abs((nx + ny) - (sx + sy)))
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]

    if best_key is None:
        return [0, 0]
    return best_move
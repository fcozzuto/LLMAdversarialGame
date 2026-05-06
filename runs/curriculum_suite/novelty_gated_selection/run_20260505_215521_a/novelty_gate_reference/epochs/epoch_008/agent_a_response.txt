def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Drift toward center while keeping distance from opponent
        cx, cy = w // 2, h // 2
        best = (-10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            score = cheb(nx, ny, cx, cy) * (-0.15) + cheb(nx, ny, ox, oy) * (0.05)
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Predict opponent target: resource with minimal opponent distance (deterministic tie-break)
    opp_best = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        key = (d, rx, ry)
        if opp_best is None or key < opp_best[0]:
            opp_best = (key, (rx, ry))
    (tx, ty) = opp_best[1]

    # Choose move that improves advantage for the predicted target, then gently prefers nearer other resources
    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # Advantage: larger is better; strong bonus for being at/near target.
        adv = (oppd - myd) * 2.2
        if myd == 0:
            adv += 80.0
        if myd <= 1:
            adv += 8.0

        # If already blocked/poor, slightly favor any resource closer than opponent by margin
        aux = 0.0
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            if d1 <= d2:
                aux = max(aux, (d2 - d1) * 0.6 - 0.05 * d1)
        # Small tie-break: avoid getting too close to opponent while approaching target
        avoid = -0.03 * cheb(nx, ny, ox, oy)
        score = adv + aux + avoid
        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]
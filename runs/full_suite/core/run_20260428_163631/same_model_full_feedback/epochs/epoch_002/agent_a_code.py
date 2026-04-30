def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def clamp_move(x, y):
        return [x if 0 <= x < w else (0 if x < 0 else w - 1),
                y if 0 <= y < h else (0 if y < 0 else h - 1)]

    # If no resources, drift to reduce opponent's advantage by approaching the opponent's resource-likely area:
    if not resources:
        tx = sx + (1 if ox < sx else (-1 if ox > sx else 0))
        ty = sy + (1 if oy < sy else (-1 if oy > sy else 0))
        tx, ty = clamp_move(tx, ty)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny):
                continue
            v = -cheb((nx, ny), (tx, ty))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Score candidate move by looking at resulting position's strongest resource takeover potential,
    # with tie-breakers to avoid obstacles and move closer.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        # Potential: sum over top few resources of (opponent_dist - my_dist), penalize giving opponent a closer lead.
        myd_best = 10**9
        pot_best = -10**18
        for r in resources:
            rx, ry = r
            myd = cheb((nx, ny), (rx, ry))
            opd = cheb((ox, oy), (rx, ry))
            takeover = opd - myd  # positive if we are closer than opponent
            if takeover > pot_best:
                pot_best = takeover
                myd_best = myd

        # Additional deterministic preferences:
        # - If we can be closer than opponent (takeover>0), prefer smaller my distance to that resource.
        # - Otherwise, still prefer moving toward resources where we reduce opponent's lead.
        # - Mild penalty for moving away from center (keeps paths stable).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = int(abs(nx - cx) + abs(ny - cy))

        v = pot_best * 100 - myd_best
        v -= center_pen

        # If opponent is adjacent, also include slight repulsion to avoid immediate contest flip.
        if cheb((ox, oy), (nx, ny)) == 1:
            v -= 25

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]
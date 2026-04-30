def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource: maximize our closeness advantage over opponent
    best_t = None
    best_adv = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer (or opponent farther)
        # small tie-break: prefer resources that are closer overall
        score = adv * 100 - (ds + do)
        if score > best_adv:
            best_adv = score
            best_t = (rx, ry)

    if best_t is None:
        # No resources: head toward farthest corner from opponent (deterministic)
        targets = [(0, 0), (0, h-1), (w-1, 0), (w-1, h-1)]
        best = None
        bestd = -1
        for tx, ty in targets:
            d = cheb(tx, ty, ox, oy)
            if d > bestd:
                bestd = d
                best = (tx, ty)
        best_t = best

    tx, ty = best_t

    # Evaluate candidate moves
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        ds = cheb(nx, ny, tx, ty)
        cur_ds = cheb(sx, sy, tx, ty)
        # Prefer getting closer to target; strongly penalize moving away
        progress = cur_ds - ds

        # Try to avoid giving opponent immediate access to us
        dist_to_opp = cheb(nx, ny, ox, oy)
        opp_near_pen = 0
        if dist_to_opp <= 1:
            opp_near_pen = 3

        # Slightly encourage reducing opponent distance to the same target (to contest less/ more?)
        do = cheb(ox, oy, tx, ty)
        do_next = cheb(ox, oy, tx, ty)  # opponent not moving now; keep constant
        # Resource contention: prefer moves that widen advantage (self closer than opponent)
        self_adv = do - ds

        # Deterministic tie-break: prefer lexicographically smaller move among equals
        score = progress * 10 + self_adv * 3 - opp_near_pen
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
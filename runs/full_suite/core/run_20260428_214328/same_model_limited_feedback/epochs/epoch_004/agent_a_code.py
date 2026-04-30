def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def best_target():
        if not resources:
            return None
        opp = (ox, oy)
        me = (sx, sy)
        best = None
        best_key = None
        for r in resources:
            rs = dist_cheb(me, r)
            ro = dist_cheb(opp, r)
            # Prefer resources we reach earlier; otherwise still consider, but less.
            key = (rs - 0.85 * ro, rs, abs(r[0] - me[0]) + abs(r[1] - me[1]))
            if best_key is None or key < best_key:
                best_key = key
                best = r
        return best

    def center_move_target():
        # deterministic center bias to prevent stalling
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        me = (sx, sy)
        best = None
        best_key = None
        for r in [(cx, cy), (cx, h - 1 - cy), (w - 1 - cx, cy), (w - 1 - cx, h - 1 - cy)]:
            key = (abs(r[0] - me[0]) + abs(r[1] - me[1]), abs(r[0] - ox) + abs(r[1] - oy))
            if best_key is None or key < best_key:
                best_key = key
                best = (int(round(r[0])), int(round(r[1])))
        if inb(best[0], best[1]):
            return best
        return (sx, sy)

    target = best_target()
    if target is None:
        target = center_move_target()

    tx, ty = target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            moves.append((dx, dy, nx, ny))

    # If target cell is occupied by obstacle, aim to reduce distance instead
    def score_move(dx, dy, nx, ny):
        if not inb(nx, ny):
            return 10**9
        if (nx, ny) in obstacles:
            return 10**8
        # Main: approach target
        my_d = dist_cheb((nx, ny), (tx, ty))
        # Secondary: avoid letting opponent approach their nearest faster
        if resources:
            opp_best = min(resources, key=lambda r: (dist_cheb((ox, oy), r), r[0], r[1]))
            opp_d = dist_cheb((ox, oy), opp_best)
            # moving increases/decreases opponent pressure slightly
            # also encourage moving toward opponent when we can't reach resources well
            pressure = 0.25 * (my_d - opp_d)
        else:
            pressure = 0
        # Tertiary: don't wander away from target quadrant
        quadrant = abs((tx - sx)) + abs((ty - sy))
        prefer = 0.02 * quadrant
        return my_d + pressure + prefer

    best = None
    best_s = None
    # Deterministic tie-break: fixed iteration order ensures stability.
    for dx, dy, nx, ny in moves:
        s = score_move(dx, dy, nx, ny)
        if best_s is None or s < best_s:
            best_s = s
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
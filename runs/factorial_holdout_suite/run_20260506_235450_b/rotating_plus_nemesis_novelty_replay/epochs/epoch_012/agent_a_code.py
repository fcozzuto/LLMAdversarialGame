def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return abs(dx) + abs(dy)

    def step_toward(tx, ty):
        best_move = [0, 0]
        best_key = None
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dtar = dist(nx, ny, tx, ty)
            dop = dist(nx, ny, ox, oy)
            # Prefer reducing target distance; if tied, prefer moving away from opponent (denial)
            key = (dtar, -dop, nx, ny)
            if best_key is None or key < best_key:
                best_key, best_move = key, [mx, my]
        return best_move

    if resources:
        # Choose a target where we're relatively closer than the opponent; if we're behind badly,
        # go for a resource farthest from the opponent to reduce their denial options.
        best_r = None
        best_key = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            advantage = (do - ds)  # positive means we are closer
            # Primary: maximize advantage; Secondary: minimize our distance; Tertiary: deterministic tie-break
            key = (-advantage, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key, best_r = key, (rx, ry)
        tx, ty = best_r
        return step_toward(tx, ty)

    # No visible resources: move to the corner that favors collecting remaining resources later.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Prefer corner closer to us, but also try to keep away from opponent's likely sweep.
    best_c = None
    best_key = None
    for cx, cy in corners:
        ds = dist(sx, sy, cx, cy)
        do = dist(ox, oy, cx, cy)
        key = (ds - do, ds, cx, cy)
        if best_key is None or key < best_key:
            best_key, best_c = key, (cx, cy)
    tx, ty = best_c

    # Greedy one-step toward chosen corner, avoid obstacles; if blocked, do best available.
    if inb(sx + 1, sy) and (sx + 1, sy) not in obstacles:
        pass  # fallthrough to generic step
    return step_toward(tx, ty)
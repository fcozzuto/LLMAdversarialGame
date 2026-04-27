def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),  (0, 0),  (0, 1),
            (1, -1),  (1, 0),  (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            d = md(nx, ny, cx, cy)
            tie = -((nx * 131 + ny) % 997)
            key = (d, tie)
            if key < (best[0], best[1]):  # deterministic
                best = (d, tie, dx * 10 + dy)
        return [best[2] // 10, best[2] % 10]

    # Choose best move by 1-step lookahead on the most contested resource
    best_key = None
    best_move = [0, 0]
    # Deterministic ordering for equal scores
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Evaluate: prefer moves that put us closer than opponent on the "best" resource
        # with a slight preference for lower absolute distance to avoid stalling.
        local_best = None
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            contest = do - ds  # positive means we are closer than opponent
            absd = ds + do
            # tie-break by resource position deterministically
            tie = (rx * 8 + ry)
            score_key = (-(contest), absd, tie)
            if local_best is None or score_key < local_best[0]:
                local_best = (score_key, rx, ry, ds, do, contest)
        _, rx, ry, ds, do, contest = local_best
        # Overall: maximize contest; secondarily minimize our distance; then reduce opponent advantage swing
        overall = (-contest, ds, (do - ds), rx * 8 + ry)
        if best_key is None or overall < best_key:
            best_key = overall
            best_move = [dx, dy]
    return best_move
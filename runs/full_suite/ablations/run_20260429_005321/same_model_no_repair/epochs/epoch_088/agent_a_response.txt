def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If no resources, drift toward center while keeping distance from opponent.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            dcent = cheb(nx, ny, cx, cy)
            dop = cheb(nx, ny, ox, oy)
            # Prefer smaller center distance and larger opponent distance
            key = (dcent, -dop, 0 if (dx == 0 and dy == 0) else 1, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # For each move, evaluate best resource we could contest:
    # lead = opp_dist - self_dist (positive means we get it sooner).
    # Add slight tie-break toward nearer resources and toward current/opponent separation.
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        best_val = None  # higher is better
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            # If ds == 0 we "take" immediately; prioritize strongly.
            take_bonus = 1000 if ds == 0 else 0
            # Encourage picking resources that are hard for opponent to reach soon (large do)
            hard = do
            val = take_bonus + 10 * lead + 0.01 * (hard) - 0.001 * ds
            if best_val is None or val > best_val:
                best_val = val
        # Secondary shaping: keep away from opponent while not stalling.
        dop = cheb(nx, ny, ox, oy)
        # Deterministic ordering: maximize best_val, then maximize dop, then prefer non-stay if close.
        key = (-best_val, -dop, 0 if (dx == 0 and dy == 0) else 1, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = 1 if sx < w // 2 else (-1 if sx > w // 2 else 0)
        ty = 1 if sy < h // 2 else (-1 if sy > h // 2 else 0)
        return [tx, ty]

    # Pick a resource you can reach earlier than the opponent (by margin), else pick best race otherwise.
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        ahead = do - ds  # positive means you are closer
        # Primary: maximize (do - ds). Secondary: minimize your distance. Tertiary: stable by coordinates.
        key = (-ahead, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res

    # Choose the move that maximizes your advantage after the move.
    best_move = (0, 0)
    best_eval = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        # Prefer: higher advantage (do2 - ds2), then lower ds2, then farther from opponent to reduce contesting impact.
        adv = do2 - ds2
        opp_sep = cheb(nx, ny, ox, oy)
        eval_key = (-adv, ds2, -opp_sep, dx, dy)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
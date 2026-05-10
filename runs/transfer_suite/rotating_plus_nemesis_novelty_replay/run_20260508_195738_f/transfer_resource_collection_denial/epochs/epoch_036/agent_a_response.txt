def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Drift to farthest corner from opponent while moving safely.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: manh(ox, oy, c[0], c[1]) - manh(sx, sy, c[0], c[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        for mx, my in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + mx, sy + my
            if valid(nx, ny):
                return [mx, my]
        return [0, 0]

    # Pick resource we can reach earlier (or tie) with largest advantage.
    best = None
    best_margin = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        margin = do - ds  # positive means we arrive sooner
        if best is None or (margin > best_margin) or (margin == best_margin and ds < best[0]):
            best = (ds, rx, ry)
            best_margin = margin

    _, tx, ty = best

    # Greedy one-step move toward target, but also prefer increasing margin.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = manh(nx, ny, tx, ty)
        do2 = manh(ox, oy, tx, ty)
        margin2 = do2 - ds2
        dist_now = manh(sx, sy, tx, ty)
        dist_next = ds2
        # Score: maximize margin first, then reduce distance, then keep movement deterministic bias.
        score = (margin2, dist_now - dist_next, -abs(dx) - abs(dy), -abs(nx - tx) - abs(ny - ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
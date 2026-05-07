def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        # deterministic drift to center-ish away from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            val = (cheb(ox, oy, nx, ny) - cheb(sx, sy, nx, ny), -cheb(nx, ny, cx, cy))
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # One-step lookahead: after our move, pick the resource that maximizes our margin
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_margin = None
        best_aux = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # positive means we are closer (tie-break by smaller ds)
            aux = (ds, cheb(nx, ny, rx, ry) + cheb(ox, oy, rx, ry))
            if best_margin is None or (margin, -aux[0], -aux[1]) > (best_margin, -best_aux[0], -best_aux[1]):
                best_margin = margin
                best_aux = aux
        # Prefer better resulting margin; tie-break by lower distance to the chosen resource after move; then by staying put
        # (deterministic: prefer smaller dx,dy lexicographically)
        chosen_ds = best_aux[0]
        lex = (abs(dx), abs(dy), dx, dy)
        val = (best_margin, -chosen_ds, -lex[0], -lex[1], -lex[2], -lex[3])
        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]
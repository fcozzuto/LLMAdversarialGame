def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            key = (cheb(nx, ny, tx, ty), cheb(ox, oy, tx, ty), nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (-(do - ds), ds, rx, ry)  # maximize advantage over opponent
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = None
    best_eval = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Prefer moves that improve our lead; if tie, prefer faster capture and safer positional tie-break.
        eval_key = (-(do2 - ds2), ds2, abs(ox - nx) + abs(oy - ny), nx, ny)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = [dx, dy]
    return best_move if best_move else [0, 0]
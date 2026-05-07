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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Choose a resource where we have time advantage, otherwise closest resource.
    best = None
    cx, cy = w // 2, h // 2
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer winning claims (ds < do). If none, minimize ds and avoid edge-hugging.
        claim = (ds - do, ds, abs(rx - cx) + abs(ry - cy), rx, ry)
        if best is None or claim < best[0]:
            best = (claim, rx, ry)
    tx, ty = best[1], best[2]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_key = None

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inside(nx, ny):
            continue
        ds_now = cheb(nx, ny, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        # Maximize immediate advantage and progress toward target.
        # Secondary: keep near center to reduce getting blocked.
        key = (do_now - ds_now, -ds_now, -cheb(nx, ny, cx, cy), mx, my)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (mx, my)

    return [best_move[0], best_move[1]]
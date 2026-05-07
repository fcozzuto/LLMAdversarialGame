def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy
    else:
        cx, cy = w // 2, h // 2
        best = None
        best_score = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            center_pen = cheb(rx, ry, cx, cy) * 0.05
            # Strongly prefer resources where we are earlier; add slight preference for central.
            score = (do - ds) * 100.0 - ds - center_pen
            # Deterministic tie-break: prefer smaller (rx,ry) then earlier distances
            key = (-score, ds, do, rx, ry)
            if best is None or key < best:
                best = key
                best_score = score
                tx, ty = rx, ry

    # Choose move that reduces distance to target and avoids obstacles.
    curd = cheb(sx, sy, tx, ty)
    best_m = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer strictly closer; then prefer closer to target; then prefer moving away from opponent.
        oppd = cheb(nx, ny, ox, oy)
        key = (-(curd > nd), nd, -oppd, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]
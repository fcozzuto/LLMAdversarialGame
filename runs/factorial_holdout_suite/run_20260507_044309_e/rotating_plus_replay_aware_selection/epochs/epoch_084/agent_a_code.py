def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target():
        if not resources:
            tx, ty = w // 2, h // 2
            return tx, ty
        best = None
        for rx, ry in resources:
            ourd = cheb(sx, sy, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Prefer resources we're closer to; if ties, prefer larger absolute advantage; then nearer.
            key = (ourd - oppd, -abs(ourd - oppd), ourd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1]

    tx, ty = best_target()
    move_order = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0), (0, 0), (1, 0),
        (-1, 1), (0, 1), (1, 1)
    ]
    curd = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_key = None
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        adv = cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)
        key = (nd - curd, adv, nd, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move
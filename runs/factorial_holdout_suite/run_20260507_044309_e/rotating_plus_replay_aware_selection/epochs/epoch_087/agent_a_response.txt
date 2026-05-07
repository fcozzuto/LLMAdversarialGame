def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources") or []
    move_order = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0), (0, 0), (1, 0),
        (-1, 1), (0, 1), (1, 1),
    ]

    def best_target():
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; if tied, prefer those with smaller own distance.
            key = (-(do - ds), ds, (rx + ry) & 1, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1]

    tgt = best_target()
    if tgt is None:
        # If no visible resources, drift toward the center row/col to reduce opponent sweep advantage.
        tx = w // 2
        ty = h // 2
        tgt = (tx, ty)

    tx, ty = tgt
    cur_ds = cheb(sx, sy, tx, ty)
    cur_adv = (cheb(ox, oy, tx, ty) - cur_ds)

    best = None
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nds = cheb(nx, ny, tx, ty)
        nd_adv = (cheb(ox, oy, tx, ty) - nds)
        # Primary: reduce distance to target; Secondary: increase lead vs opponent; Tertiary: parity bias.
        key = (nds, -(nd_adv - cur_adv), ((nx + ny) & 1), nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]
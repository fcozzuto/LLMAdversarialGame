def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles
    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best_r = None
        best_adv = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer
            if best_adv is None or adv > best_adv or (adv == best_adv and myd < md(sx, sy, best_r[0], best_r[1])):
                best_adv, best_r = adv, (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Prefer reducing distance to chosen target; also deny by making us "relatively closer"
        # and keep away from opponent slightly.
        oppd_after = md(ox, oy, tx, ty)
        # tie-break: prefer moves that increase distance to opponent
        dist_opp = md(nx, ny, ox, oy)
        key = (myd, -((opd - myd)), -dist_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
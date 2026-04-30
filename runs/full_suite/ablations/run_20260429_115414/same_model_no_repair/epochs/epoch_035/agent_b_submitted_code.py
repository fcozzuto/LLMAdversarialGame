def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Pick best resource by who can arrive earlier, with deterministic tie-breaks.
    best = None  # (adv, -sd, -od, rx, ry)
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in blocked:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        cand = (adv, -sd, -od, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        tx, ty = w // 2, h // 2
    else:
        _, _, _, tx, ty = best

    # Take one step that reduces our distance to the target, with opponent pressure and safety.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Prefer moves that improve our arrival and reduce opponent advantage; deterministic tie-break.
        val = (-(nd), (nod - nd), -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1]]]
def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    blocked = set()
    for b in observation.get("obstacles") or []:
        try:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res.append((rx, ry))
        except:
            pass
    if not res:
        return [0, 0]

    # Predictive intercept: opponent's nearest resource
    best_op = res[0]
    bo = cheb(ox, oy, best_op[0], best_op[1])
    for rx, ry in res[1:]:
        d = cheb(ox, oy, rx, ry)
        if d < bo:
            bo = d
            best_op = (rx, ry)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        # Choose best target for us from predicted next position
        best_adv = -10**18
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = (do - ds) * 1000 - ds  # strong preference to beat opponent, then shorter
            # discourage moving toward resources where opponent is already effectively equal/slightly ahead
            if ds > do:
                adv -= 300
            if adv > best_adv:
                best_adv = adv

        # Intercept pressure if we can quickly reach opponent's nearest resource
        ds_int = cheb(nx, ny, best_op[0], best_op[1])
        do_int = cheb(ox, oy, best_op[0], best_op[1])
        intercept = 0
        if ds_int <= do_int:
            intercept = (do_int - ds_int) * 800 - ds_int
        else:
            intercept = -(ds_int - do_int) * 200

        # Mild obstacle-free preference already handled; add slight bias to move toward center to reduce corner traps
        center_bias = -abs((nx - (w - 1) / 2)) - abs((ny - (h - 1) / 2))

        val = best_adv + intercept + center_bias
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
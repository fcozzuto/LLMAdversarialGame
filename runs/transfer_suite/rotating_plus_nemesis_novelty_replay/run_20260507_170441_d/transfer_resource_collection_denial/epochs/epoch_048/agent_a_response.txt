def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Target selection with row/column bias to counter sweep behavior:
    # Prefer resources whose row or column is "closer-favorable" for us.
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        row_bias = 0
        if sy == ry: row_bias -= 1
        if sx == rx: row_bias -= 1
        key = (1 if myd > opd else 0, myd - opd, myd, row_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_t = key, (rx, ry)
    tx, ty = best_t

    def opp_step_to_target(x, y, tx, ty):
        best = None
        best_d = None
        best_dd = None
        for ddx, ddy in moves:
            nx, ny = x + ddx, y + ddy
            if not inb(nx, ny):
                continue
            nd = dist(nx, ny, tx, ty)
            better = (best_d is None or nd < best_d or (nd == best_d and (ddx, ddy) < best_dd))
            if better:
                best_d = nd
                best_dd = (ddx, ddy)
                best = (nx, ny)
        return best if best is not None else (x, y)

    # Choose move that creates maximum advantage after our step and predicted opponent step.
    best_move = (0, 0)
    best_adv = None
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny):
            continue
        n_op = opp_step_to_target(ox, oy, tx, ty)
        # Advantage uses distance reduction and tie-breaker toward actual capture.
        my_after = dist(nx, ny, tx, ty)
        op_after = dist(n_op[0], n_op[1], tx, ty)
        adv = (op_after - my_after, -my_after, -dist(nx, ny, ox, oy), ddx, ddy)
        if best_adv is None or adv > best_adv:
            best_adv = adv
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]
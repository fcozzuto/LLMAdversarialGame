def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def legal_cell(x, y):
        return inb(x, y) and (x, y) not in obst

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal moves)

    if not resources:
        return [0, 0]

    best_take = None
    best_key = None
    best_contest = None
    best_contest_key = None

    for rx, ry in resources:
        if not legal_cell(rx, ry):
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - ds
        key_take = (adv, -ds, do, rx, ry)
        if best_key is None or key_take > best_key:
            best_key = key_take
            best_take = (rx, ry)
        if ds < do:
            key_cont = (do - ds, -ds, do, rx, ry)
            if best_contest_key is None or key_cont > best_contest_key:
                best_contest_key = key_cont
                best_contest = (rx, ry)

    target = best_contest if best_contest is not None else best_take
    tx, ty = target
    step_dx = 0 if tx == sx else (1 if tx > sx else -1)
    step_dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + step_dx, sy + step_dy

    if legal_cell(nx, ny):
        return [step_dx, step_dy]

    # Fallback: choose best legal neighbor toward target with minimal impact
    best_m = None
    best_m_key = None
    for dx, dy in moves:
        cx, cy = sx + dx, sy + dy
        if not legal_cell(cx, cy):
            continue
        d1 = dist(cx, cy, tx, ty)
        d_opp = dist(ox, oy, tx, ty)
        my_after = d1
        adv_after = d_opp - my_after
        key = (adv_after, -my_after, dx, dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)
    return [best_m[0], best_m[1]]
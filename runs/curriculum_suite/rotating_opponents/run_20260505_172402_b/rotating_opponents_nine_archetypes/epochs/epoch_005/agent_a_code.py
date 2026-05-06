def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()  # deterministic tie-break

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def step_towards(px, py, tx, ty):
        dx = 0 if tx == px else (1 if tx > px else -1)
        dy = 0 if ty == py else (1 if ty > py else -1)
        return px + dx, py + dy

    def dist(a, b, c, d):
        return abs(c - a) + abs(d - b)

    # Strategic shift: contest resources where opponent is closer (corner_guard),
    # otherwise go for best relative gain.
    best = None
    best_key = None
    d_opp = dist(sx, sy, ox, oy)
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        rel = opd - myd  # want large positive (I'm closer)
        # If opponent is very close to me, prioritize denying its nearest resources.
        if d_opp <= 3:
            rel = (opd - myd) * 2 - myd * 0.5
        # If I'm far but opponent is closer, heavily bias contesting.
        if opd < myd:
            rel = rel * 2 - (myd - opd) * 1.5
        # Mild preference to approach resources that are also closer to the board center (reduces corner lock).
        center_bias = -0.1 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
        key = (rel + center_bias, -myd)  # maximize rel, then minimize myd
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    # If no resources, move toward opponent's potential line by heading to center.
    if best is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    nx, ny = step_towards(sx, sy, tx, ty)

    if valid(nx, ny):
        return [nx - sx, ny - sy]

    # Otherwise, choose best valid move by minimizing (distance to target) and avoiding moving toward opponent when it is close.
    best_mv = (0, 0)
    best_val = None
    for dx, dy in moves:
        x, y = sx + dx, sy + dy
        if not valid(x, y):
            continue
        my_to_t = dist(x, y, tx, ty)
        to_opp = dist(x, y, ox, oy)
        # If contesting: don't let opponent proximity improve too much.
        penalty = 0
        if d_opp <= 3:
            penalty = (3 - min(3, to_opp)) * 2.0
        val = (my_to_t, penalty, abs(dx) + abs(dy))
        if best_val is None or val < best_val:
            best_val = val
            best_mv = (dx, dy)
    return [best_mv[0], best_mv[1]]
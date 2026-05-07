def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    # Pick a target resource that we can reach relatively earlier than opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # positive => we are closer
        # Tie-break: prefer closer to us, and slightly prefer resources in our current row/col.
        align = (1 if rx == sx else 0) + (1 if ry == sy else 0)
        key = (-adv, sd, -align, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None
    sd0 = md(sx, sy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd1 = md(nx, ny, tx, ty)
        # Primary: move reduces our distance to target; secondary: improve relative advantage.
        od1 = md(ox, oy, tx, ty)
        rel = od1 - sd1
        step_improve = sd1 - sd0  # negative is good
        # Small bias: avoid stepping into rows/cols where opponent is likely sweeping (their current row/col).
        row_bias = 0 if ny != oy else -0.15
        col_bias = 0 if nx != ox else -0.15
        score = (step_improve, -rel, sd1, row_bias + col_bias, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
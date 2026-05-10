def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Pick a target we can reach at least as fast as (or faster than) opponent; otherwise best race.
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        adv = do - ds  # positive => we are closer
        key = (0 if adv >= 0 else 1, -adv, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    best_move = (0, 0)
    best_score = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        # Score: maximize advantage (opp-self), then minimize our distance to the target.
        adv2 = do2 - ds2
        # Secondary: discourage stepping away from target and slightly prefer moves that don't increase opp advantage too much against us.
        score = (adv2, -ds2, -abs(nx - tx) - abs(ny - ty), -dxm, -dym)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def target_score(tx, ty):
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        adv = do - ds  # larger is better for us
        # tie-break: prefer nearer self and slightly prefer farther from opponent (more tempo)
        return (adv, -ds, do)

    if not resources:
        return [0, 0]

    # Choose resource with maximal predicted capture advantage.
    best = None
    best_key = None
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        key = target_score(rx, ry)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key
    if best is None:
        # If all resources blocked, just avoid obstacles while making progress toward any resource.
        rx, ry = resources[0]
        tx, ty = rx, ry
    else:
        tx, ty = best

    # Move toward target, but maximize resulting capture advantage.
    best_move = (0, 0)
    best_eval = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue
        ds2 = dist(nx, ny, tx, ty)
        do2 = dist(ox, oy, tx, ty)
        adv2 = do2 - ds2
        # Prefer fewer steps to target; and avoid moves that reduce advantage too much.
        ev = (adv2, -ds2, -abs(nx - ox) - abs(ny - oy))
        if best_eval is None or ev > best_eval:
            best_eval = ev
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]
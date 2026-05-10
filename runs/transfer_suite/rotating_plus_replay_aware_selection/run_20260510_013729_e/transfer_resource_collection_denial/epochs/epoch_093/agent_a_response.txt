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

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Prefer resources where we gain tempo over the opponent, but avoid ones too close to opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Lower is better: (we want ds<=do, but also not giving opponent an easy alternative)
        # Add small bias for closer absolute ds to finish earlier.
        key = (ds - (do // 2), ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Deterministic obstacle-aware step: among legal moves, minimize (distance to target, distance advantage vs opponent after move)
    chosen = None
    chosen_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ns = man(nx, ny, tx, ty)
        no = man(ox, oy, tx, ty)
        # Opponent is "nearest resource"; encourage maintaining or increasing our advantage.
        adv_key = (ns, (ns - (no // 2)), abs(nx - ox) + abs(ny - oy), dx, dy)
        if chosen_key is None or adv_key < chosen_key:
            chosen_key = adv_key
            chosen = (dx, dy)

    if chosen is None:
        return [0, 0]
    return [int(chosen[0]), int(chosen[1])]
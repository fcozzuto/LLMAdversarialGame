def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def adj_obst(nx, ny):
        # small deterrent from tight corners / obstacle-adjacent traps
        for dx, dy in deltas:
            ax, ay = nx + dx, ny + dy
            if (ax, ay) in obstacles:
                return 1
        return 0

    valid_targets = [(rx, ry) for rx, ry in resources if inb(rx, ry) and (rx, ry) not in obstacles]
    if not valid_targets:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    # Pick a target where we can "out-reach" the opponent (or at least reduce the deficit)
    best_target = None
    best_tie = None
    for tx, ty in valid_targets:
        myd = man(sx, sy, tx, ty)
        opd = man(ox, oy, tx, ty)
        adv = opd - myd
        # prefer positive advantage; if none, minimize how far behind we are; tie-break by closer to center-ish
        tie = (-1 if adv > 0 else 0, -adv, myd, abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2))
        if best_tie is None or tie < best_tie:
            best_tie = tie
            best_target = (tx, ty)

    tx, ty = best_target
    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        # advantage from prospective position
        opd = man(ox, oy, tx, ty)
        adv = opd - myd
        # main key: maximize advantage; then minimize our distance; then avoid obstacle-adjacency
        key = (-(1 if adv > 0 else 0), -adv, myd, adj_obst(nx, ny), abs(nx - tx) + abs(ny - ty))
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move
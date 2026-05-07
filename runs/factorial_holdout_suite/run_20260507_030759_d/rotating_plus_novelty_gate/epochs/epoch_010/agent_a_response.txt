def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target selection: prioritize resources we can reach no later than opponent; otherwise prefer bigger advantage.
    # Tie-break deterministically by closer-to-us, then farther-from-them, then position.
    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Primary: prefer ds - do smaller (we earlier), strongly prefer negative.
        lead = ds - do
        key = (lead, ds, -do, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # One-step: choose legal move that minimizes our (ds-do) to the target after the move.
    # Slight bias to reduce distance to target to avoid dithering.
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        # If target is blocked by stepping onto it? It's allowed; landing on resource likely collects.
        # Bias: prefer smaller ds2, and avoid moving away from target.
        key = (ds2 - do2, ds2, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
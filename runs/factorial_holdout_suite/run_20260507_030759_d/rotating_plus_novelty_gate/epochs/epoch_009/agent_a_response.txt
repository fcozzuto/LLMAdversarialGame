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
    if not legal or not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick target deterministically by maximizing advantage and desirability.
    best_target = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Lower is better for key: want sd-od small/negative, then closer, then farther from opponent.
        key = (sd - od, sd, -od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # One-step lookahead toward (tx,ty) while not walking into obvious contest disadvantage.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Encourage faster arrival and also avoid increasing my distance relative to opponent.
        # Add tiny tie-break: prefer staying aligned closer to target direction.
        align = -(abs((tx - nx) - (tx - ox)) + abs((ty - ny) - (ty - oy)))
        key = (myd - opd, myd, -opd, -align, nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
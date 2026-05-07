def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a target: prefer resources we can reach no later than opponent; otherwise pick best gap.
    best = None
    for rx, ry in resources:
        sd = md(x, y, rx, ry)
        od = md(ox, oy, rx, ry)
        if sd <= od:
            key = (0, sd, od, rx, ry)
        else:
            key = (1, -(od - sd), sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Also estimate opponent's likely target to slightly discourage letting them close.
    obest = None
    for rx, ry in resources:
        sd = md(ox, oy, rx, ry)
        od = md(x, y, rx, ry)
        key = (sd, -od, rx, ry)
        if obest is None or key < obest[0]:
            obest = (key, (rx, ry))
    otx, oty = obest[1]

    best_mv = [0, 0]
    best_sc = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        sd = md(nx, ny, tx, ty)
        od = md(ox, oy, tx, ty)
        # Prefer reducing our distance to our target; and increase their distance to our target.
        sc = (sd, -od, md(nx, ny, otx, oty), -md(ox, oy, otx, oty), dx, dy)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_mv = [dx, dy]

    return best_mv
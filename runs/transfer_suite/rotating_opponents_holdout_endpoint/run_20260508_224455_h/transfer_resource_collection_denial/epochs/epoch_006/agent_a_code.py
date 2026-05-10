def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target choice: prioritize resources where we can be closer than opponent (or least bad when contested).
    best = None  # (key, tx, ty)
    for rx, ry in resources:
        my = man(sx, sy, rx, ry)
        ot = man(ox, oy, rx, ry)
        # key: lower is better. Prefer positive swing (ot - my), strongly when we are currently closer/equal.
        if my <= ot:
            gain = ot - my
            key = (-1, -gain, my, ot, rx, ry)
        else:
            # we're behind: still chase, but minimize how far behind and keep ot small enough to contest soon
            key = (0, my - ot, ot, my, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    # Move choice: step toward target; if tied, improve relative position vs opponent; avoid obstacles.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    bestm = None  # (key, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        my_cur = man(sx, sy, tx, ty)
        od_cur = man(sx, sy, ox, oy) if (sx, sy) != (ox, oy) else 0
        od_next = man(nx, ny, ox, oy)
        # key: primarily reduce distance to target; secondarily ensure we don't get worse vs opponent too much.
        rel_cur = my_cur - man(ox, oy, tx, ty)
        rel_next = myd - man(ox, oy, tx, ty)
        key = (myd, rel_next, -(od_next), dx, dy)
        if bestm is None or key < bestm[0]:
            bestm = (key, dx, dy)

    return [bestm[1], bestm[2]]
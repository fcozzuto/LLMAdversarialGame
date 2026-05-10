def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # If no resources, just stay (should be rare).
    if not resources:
        return [0, 0]

    # Pick a target: prefer resources we can reach strictly sooner; otherwise deny by maximizing opponent delay.
    best = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # key: (we_reach_first, -advantage, myd, opd)
        # we_reach_first: 0 if good else 1 (lower is better)
        we = 0 if myd <= opd else 1
        adv = (opd - myd)  # positive favors us reaching first
        # Slight tie-break: closer is better when similarly secure/deniable.
        key = (we, -adv, myd, opd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Move: choose step that keeps (or improves) advantage; avoid stepping into obstacles.
    bestm = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        we = 0 if myd <= opd else 1
        adv = opd - myd  # positive means we are closer than opponent
        # Secondary: after moving, if opponent currently is very close to target, prioritize denying.
        key = (we, -adv, myd, abs((ox - nx)) + abs((oy - ny)), dx, dy)
        if bestm is None or key < bestm[0]:
            bestm = (key, [dx, dy])

    if bestm is None:
        return [0, 0]
    return bestm[1]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick resource where we are at least as close as opponent; otherwise contest nearest-ish.
    best = None  # (pr, my, ot, rx, ry)
    for rx, ry in resources:
        my = man(sx, sy, rx, ry)
        ot = man(ox, oy, rx, ry)
        if my == 0 and (sx, sy) == (rx, ry):
            pr = -10**9
        else:
            pr = (0 if my <= ot else 1) * 10**7 + (my - ot)
        cand = (pr, my, ot, rx, ry)
        if best is None or cand < best:
            best = cand
    _, _, _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Avoid stepping into obstacles; choose move that reduces distance to target, with tie-break on opponent.
    bestm = None  # (score, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        # Prefer getting closer than opponent to same target.
        opd = man(ox, oy, tx, ty)
        # Small bias: if our move would make us worse than opponent, avoid unless it helps greatly.
        score = myd * 10**3 + (0 if myd <= opd else 500) + (opd - myd)
        if bestm is None or score < bestm[0]:
            bestm = (score, dx, dy)

    if bestm is not None:
        return [int(bestm[1]), int(bestm[2])]

    # If all adjacent are blocked (unlikely), stay.
    return [0, 0]
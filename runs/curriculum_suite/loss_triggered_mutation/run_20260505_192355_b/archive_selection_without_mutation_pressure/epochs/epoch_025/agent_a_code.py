def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # Pick a target where we are not behind, else pick the least-bad option.
    best_target = None
    best_key = None
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        if opd >= myd:
            key = (0, myd, opd - myd)  # prioritize closer when not behind
        else:
            key = (1, -(opd - myd), myd)  # prioritize least disadvantage / quickest progress
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    opp_close = (manh(sx, sy, ox, oy) <= 2)

    # Evaluate each immediate move with a contestedness heuristic.
    best_move = valid[0]
    best_score = None
    for dx, dy, nx, ny in valid:
        best_adv = -10**9
        best_myd = None
        dist_to_target = manh(nx, ny, tx, ty)
        for rx, ry in resources:
            myd = manh(nx, ny, rx, ry)
            opd = manh(ox, oy, rx, ry)
            adv = opd - myd
            if adv > best_adv:
                best_adv = adv
                best_myd = myd
        dist_from_opp = manh(nx, ny, ox, oy)
        score = (best_adv * 10) - dist_to_target
        if opp_close and best_adv <= 0:
            score += dist_from_opp  # don't walk into denier proximity if we're not gaining contests
        if best_score is None or score > best_score or (score == best_score and dist_to_target < manh(sx, sy, tx, ty)):
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]
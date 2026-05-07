def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Choose best next step by evaluating best target resource advantage after the move.
    best = None
    best_move = [0, 0]
    res_sorted = sorted(resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # For this candidate move, pick the resource we would most likely secure.
        # Key favors: (selfdist - oppdist) smaller -> opp farther, then smaller selfdist.
        best_key_for_move = None
        for rx, ry in res_sorted:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            key = (myd - opd, myd, rx, ry)
            if best_key_for_move is None or key < best_key_for_move:
                best_key_for_move = key

        # Also prefer moves that slightly reduce opp's best advantage directly.
        # (Try to "deny" by heading toward resources that are currently more favorable to us.)
        myd_after = best_key_for_move[1]
        opp_adv = best_key_for_move[0]
        global_key = (opp_adv, myd_after, dx, dy)
        if best is None or global_key < best:
            best = global_key
            best_move = [dx, dy]

    return best_move
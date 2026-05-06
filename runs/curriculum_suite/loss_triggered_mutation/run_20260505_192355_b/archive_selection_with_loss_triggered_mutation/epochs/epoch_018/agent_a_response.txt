def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    # Choose a move that improves "we arrive sooner" on some resource; otherwise push to deny by approaching opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Evaluate best target for us from this next position.
        # Prefer: (opp_eta - my_eta) high, then close my_eta, then absolute priority by remaining.
        best_local = None
        for tx, ty in resources:
            my_eta = md(nx, ny, tx, ty)
            opp_eta = md(ox, oy, tx, ty)
            # if we can beat opponent, score strongly
            margin = opp_eta - my_eta
            # also slightly prefer resources that are far from opponent to reduce sweep advantage
            opp_prox = -md(ox, oy, tx, ty)
            cand = (margin, -my_eta, opp_prox, tx, ty)
            if best_local is None or cand > best_local:
                best_local = cand

        margin, neg_my_eta, opp_prox, tx, ty = best_local
        # Secondary objective: if margins are small, move to align with a row-contest (opponent sweep_rows tendency)
        row_bias = -abs((ny - ox) - (sy - oy))  # deterministic slight preference based on relative row movement
        # Also discourage staying if a move can improve margin.
        cand_overall = (margin, neg_my_eta, row_bias, -abs(nx - tx), -abs(ny - ty), nx, ny)
        if best is None or cand_overall > best:
            best = cand_overall
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move
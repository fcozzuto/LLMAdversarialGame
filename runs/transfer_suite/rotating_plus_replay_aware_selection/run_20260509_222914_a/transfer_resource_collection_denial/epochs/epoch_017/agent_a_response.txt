def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    move_order = {d: i for i, d in enumerate(deltas)}

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(a, b, c, d):
        v = a - c
        u = b - d
        if v < 0:
            v = -v
        if u < 0:
            u = -u
        return v + u

    if not resources:
        tx, ty = (w - 1, 0) if (ox <= w // 2) else (0, h - 1)
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        candidates = [(dx, 0), (0, dy), (dx, dy), (0, 0)]
        for dx1, dy1 in candidates:
            nx, ny = x + dx1, y + dy1
            if inb(nx, ny):
                return [dx1, dy1]
        return [0, 0]

    best = -10**18
    best_moves = []

    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            continue

        # Evaluate move by best achievable "lead" over opponent after the move.
        # Lead = opponent_dist - our_dist_next (bigger is better).
        lead = -10**18
        best_our_dist = 10**9
        for rx, ry in resources:
            our_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            l = opp_d - our_d
            if l > lead or (l == lead and our_d < best_our_dist):
                lead = l
                best_our_dist = our_d

        # Small preference for closer progress to reduce oscillation.
        cx, cy = w // 2, h // 2
        prog = -best_our_dist - (md(nx, ny, cx, cy) * 0.01)
        score = lead + prog

        if score > best:
            best = score
            best_moves = [(dx0, dy0)]
        elif score == best:
            best_moves.append((dx0, dy0))

    # Deterministic tie-break by fixed order.
    best_moves.sort(key=lambda d: move_order[d])
    dx0, dy0 = best_moves[0]
    return [dx0, dy0]
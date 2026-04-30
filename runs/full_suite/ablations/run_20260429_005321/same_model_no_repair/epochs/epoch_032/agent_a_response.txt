def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def opp_min_dist(rx, ry):
        best = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                d = man(nx, ny, rx, ry)
                if best is None or d < best:
                    best = d
        return best if best is not None else man(ox, oy, rx, ry)

    # Pick a target resource using an estimated "race" against the opponent (their next-step min distance).
    bestT = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do1 = opp_min_dist(rx, ry)
        # Prefer: we are closer (do1 - ds large). If tied, prefer smaller ds, then deterministic coordinate.
        val = (do1 - ds) * 10000 - ds * 10 - (rx * 11 + ry)
        if bestT is None or val > bestT[0]:
            bestT = (val, rx, ry, ds, do1)
    _, tx, ty, _, _ = bestT

    # Choose our move: minimize our distance to target while accounting for opponent's race after their next move.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = opp_min_dist(tx, ty)
        # Encourage winning the race; slight penalty for moving away from target; avoid stepping that reduces our margin.
        score = (d_opp - d_self) * 10000 - d_self * 20 - (abs(nx - sx) + abs(ny - sy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]
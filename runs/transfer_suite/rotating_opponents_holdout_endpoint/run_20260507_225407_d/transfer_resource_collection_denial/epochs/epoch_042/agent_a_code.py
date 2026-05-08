def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def step_ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    # Pick a target resource deterministically by "win-likelihood": prefer where we beat opponent arrival.
    best_val = None
    best_t = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        tx, ty = r[0], r[1]
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        ds = abs(sx - tx) + abs(sy - ty)
        do = abs(ox - tx) + abs(oy - ty)
        # Higher is better: we want ds<=do (or at least close), and also shorter paths to reduce opponent steals later.
        v = (do - ds) * 100 - ds * 2 - do
        if best_val is None or v > best_val or (v == best_val and (tx, ty) < best_t):
            best_val, best_t = v, (tx, ty)

    if best_t is None:
        # No known safe resources: drift toward farthest corner from opponent to reduce contesting.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy) - (abs(c[0] - sx) + abs(c[1] - sy)) * 0.01)
        target = (tx, ty)
    else:
        target = best_t

    tx, ty = target
    # Evaluate next moves by expected advantage at the next step.
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        ds1 = abs(nx - tx) + abs(ny - ty)
        do1 = abs(ox - tx) + abs(oy - ty)
        # Also, discourage moving away from overall resource set: consider nearest resource from next pos.
        near = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) == 2):
                continue
            rx, ry = r[0], r[1]
            if inb(rx, ry) and (rx, ry) not in obs:
                d = abs(nx - rx) + abs(ny - ry)
                if near is None or d < near:
                    near = d
        near_term = 0 if near is None else -near
        score = (do1 - ds1) * 100 - ds1 * 3 + near_term
        # Tie-break deterministically by move ordering.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    # If all moves invalid (shouldn't happen), stay.
    return best_move if best_move is not None else [0, 0]
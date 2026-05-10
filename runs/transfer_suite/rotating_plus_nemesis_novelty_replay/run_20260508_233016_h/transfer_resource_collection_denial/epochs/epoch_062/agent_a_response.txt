def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev (diagonals allowed)
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Choose a target that we can reach much sooner than opponent; if tie, go for closer and more "disruptive".
    best = None
    best_key = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        margin = opd - myd  # positive if we are closer
        # Encourage blocking moves: prefer targets closer to opponent than us (negative margin) only if also close to us.
        key = (-(margin > 0), -margin, myd, opd - myd, (rx + ry) & 1, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Prefer the move that reduces Chebyshev distance to target, but also maximizes our lead over opponent.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = dist(nx, ny, tx, ty)
        myd_opp = dist(nx, ny, ox, oy)
        # Lead if we follow toward target (target-focused), plus a small penalty for moving away from opponents’ threat line.
        lead = dist(ox, oy, tx, ty) - myd2
        key = (-lead, myd2, -myd_opp, abs(nx - ox) + abs(ny - oy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
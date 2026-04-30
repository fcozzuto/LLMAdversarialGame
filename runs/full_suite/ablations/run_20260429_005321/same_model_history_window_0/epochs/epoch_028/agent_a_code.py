def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    best_moves = []
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def target_score(tx, ty):
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources we are closer to; slightly penalize being behind.
        return ds - 0.55 * do

    # Pick a target resource deterministically: minimal target_score, tie by coordinates.
    best_t = None
    best_sc = None
    for r in resources:
        tx, ty = r[0], r[1]
        sc = target_score(tx, ty)
        if best_sc is None or sc < best_sc or (sc == best_sc and (tx, ty) < best_t):
            best_sc = sc
            best_t = (tx, ty)
    tx, ty = best_t

    # Evaluate all moves toward that target with opponent-aware tie-break.
    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            val = -10**9
        else:
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            # If opponent is also competing, slow down if we'd fall behind.
            val = -self_d + 0.18 * (opp_d - self_d)
            # Small bias to reduce distance in general.
            val += 0.01 * (-(cheb(nx, ny, sx, sy)))
            # Prefer staying only if necessary.
            if dx == 0 and dy == 0:
                val -= 0.05
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val and best is not None:
            # Deterministic tie-break: lexicographically smaller delta.
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]
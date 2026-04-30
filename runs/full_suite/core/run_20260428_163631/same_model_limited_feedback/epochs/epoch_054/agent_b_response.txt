def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev, supports diagonals

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Pick a target resource deterministically: prefer closer to self and farther from opponent.
    if resources:
        best = None
        best_val = -10**9
        for r in resources:
            rv = -dist((sx, sy), r) + 0.35 * dist((ox, oy), r)
            if rv > best_val:
                best_val = rv
                best = r
        tx, ty = best
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    # Evaluate immediate moves.
    best_moves = []
    best_score = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Primary: move closer (or not away) from target.
        if resources:
            d_before = dist((sx, sy), (tx, ty))
            d_after = dist((nx, ny), (tx, ty))
            primary = (d_before - d_after) * 2.0  # positive if closer
        else:
            # center-seeking
            cb = -max(abs(sx - tx), abs(sy - ty))
            ca = -max(abs(nx - tx), abs(ny - ty))
            primary = ca - cb

        # Secondary: avoid being too close to opponent when not improving much.
        opp_close = dist((nx, ny), (ox, oy))
        safety = opp_close * 0.03

        # Tiebreaker: deterministic order preference that also reduces randomness-like behavior.
        # Prefer moves with smaller dx,dy lexicographically.
        tie = -((dx + 1) * 10 + (dy + 1)) * 1e-6

        score = primary + safety + tie
        if score > best_score + 1e-12:
            best_score = score
            best_moves = [(dx, dy)]
        elif abs(score - best_score) <= 1e-12:
            best_moves.append((dx, dy))

    # Final deterministic tie-break: choose lexicographically smallest among tied moves.
    best_moves.sort()
    return [best_moves[0][0], best_moves[0][1]]
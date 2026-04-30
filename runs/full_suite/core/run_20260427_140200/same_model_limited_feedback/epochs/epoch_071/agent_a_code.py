def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    # Pick target resource: prefer those where we are closer than opponent
    best = None
    for r in resources:
        rv = dist2((sx, sy), tuple(r)) - dist2((ox, oy), tuple(r))
        # tie-break deterministically by coordinates
        key = (rv, r[1], r[0])
        if best is None or key < best[0]:
            best = (key, tuple(r))
    target = best[1] if best is not None else (w//2, h//2)

    # Choose best move toward target with obstacle avoidance and mild anti-collision
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = dist2((nx, ny), target)
        opd = dist2((nx, ny), (ox, oy))
        # discourage moving adjacent/onto opponent; still allow if needed
        score = myd - 0.15 * opd
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"] or []
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    # Choose a target resource that we are likely to reach earlier than opponent.
    if resources:
        best = None
        for r in resources:
            rp = (r[0], r[1])
            my_eta = dist((sx, sy), rp)
            op_eta = dist((ox, oy), rp)
            # Prefer: we arrive sooner; then shorter ETA; then deterministic tie-break.
            key = (-(my_eta - op_eta), -my_eta, rp[0], rp[1])
            if best is None or key > best[0]:
                best = (key, rp)
        target = best[1]
    else:
        # No visible resources: drift toward center to reduce being trapped.
        target = (w//2, h//2)

    # One-step look: among legal moves, pick one that reduces distance to target and improves relative progress.
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = None
    best_key = None
    for dx, dy, nx, ny in legal:
        my_d = dist((nx, ny), target)
        op_d = dist((ox, oy), target)
        # Prefer smaller my distance; then being closer relative to opponent; then deterministic tie-break.
        key = (-my_d, -(my_d - op_d), dx, dy, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
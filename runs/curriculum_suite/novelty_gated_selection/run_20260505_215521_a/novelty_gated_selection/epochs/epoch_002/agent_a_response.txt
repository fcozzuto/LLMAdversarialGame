def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obst = set((p[0], p[1]) for p in obstacles)
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    target = None
    if resources:
        best = None
        for r in resources:
            sd = dist2((sx, sy), r)
            od = dist2((ox, oy), r)
            # Prefer resources where we are relatively closer; deterministic tie-break by coords.
            score = sd - od
            cand = (score, r[0], r[1])
            if best is None or cand < best:
                best = cand
        target = (best[1], best[2])

    # If no good target (or none exist), switch to opponent-blocking behavior.
    chase_mode = (target is None)
    if target is not None and resources:
        my_ahead = dist2((sx, sy), target) <= dist2((ox, oy), target)
        chase_mode = not my_ahead

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        if chase_mode:
            # Block/deny: minimize distance to opponent (reduce their escape).
            val = dist2((nx, ny), (ox, oy))
        else:
            # Opportunistic but oppositional-aware: prioritize target while keeping close to opponent.
            val = dist2((nx, ny), target) + 0.5 * dist2((nx, ny), (ox, oy))

        # Deterministic tie-break prefers smaller dx, then dy.
        key = (val, dx, dy)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
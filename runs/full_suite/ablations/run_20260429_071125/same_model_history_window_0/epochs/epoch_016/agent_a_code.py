def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    # If no resources, drift toward center to reduce being trapped
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    # Choose a resource where we are relatively closer than opponent; avoid those "owned" by opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        ahead = do - ds  # higher => we are closer
        # Prefer closer overall among equal ahead; deterministic tie-break by position
        key = (ahead, -ds, -(rx * 31 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Move: pick legal step minimizing distance to target, with obstacle penalty and slight opponent interference.
    def score_step(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        nt = dist((nx, ny), (tx, ty))
        nn = dist((nx, ny), (ox, oy))
        # If opponent is very close to the target, we bias toward being a bit farther from opponent to avoid collisions.
        ds = dist((sx, sy), (tx, ty))
        do = dist((ox, oy), (tx, ty))
        opponent_close = 1 if do <= ds else 0
        return (-(nt * 10) + (nn * (-1 if opponent_close else 0)) + (1 if (nx, ny) == (tx, ty) else 0))

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic preference order
    for dx, dy in sorted(deltas, key=lambda t: (t[0] != 0, t[1] != 0, t[0], t[1])):
        v = score_step(dx, dy)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
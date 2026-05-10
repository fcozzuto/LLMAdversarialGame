def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid_next(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    # Target resources where we have a clear distance advantage (or can secure one earlier).
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer: we are closer/equal; else strongly penalize.
        # Also prefer nearer targets when advantage is similar.
        adv = do - ds
        key = (0 if adv >= 0 else 1, -adv, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    tx, ty = best[1], best[2]

    # Choose move that heads toward target while staying valid; tie-break deterministically.
    candidates = []
    for dx, dy in moves:
        if not valid_next(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        d = man(nx, ny, tx, ty)
        # Add small term to avoid dithering around opponent by biasing slightly away if very contested.
        d_op = man(nx, ny, ox, oy)
        candidates.append((d, -d_op, dx == 0 and dy == 0, dx, dy))
    if not candidates:
        # No valid moves (rare): deterministic safe fallback: stay.
        return [0, 0]

    candidates.sort()
    dx, dy = candidates[0][3], candidates[0][4]
    return [int(dx), int(dy)]
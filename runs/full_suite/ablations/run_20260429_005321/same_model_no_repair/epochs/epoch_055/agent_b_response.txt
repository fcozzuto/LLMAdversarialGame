def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_obs_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    # Choose a target that we can contest (or at least race) deterministically.
    best_t = None
    best_key = None
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Prefer (1) contested reach, (2) closing gap, (3) nearer target, (4) safer neighborhood.
        key = (
            1 if myd <= opd else 0,
            opd - myd,
            -myd,
            -adj_obs_pen(tx, ty),
            -md(tx, ty, (w - 1) // 2, (h - 1) // 2),
            tx,
            ty,
        )
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Move: minimize our distance to target; if tied, keep away from opponent; avoid obstacles.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = md(nx, ny, tx, ty)
        # Defensive tie-break: prefer moves that increase distance from opponent (avoid easy contests).
        opp_sep = md(nx, ny, ox, oy)
        # Small preference for safer squares.
        val = (
            -myd2,              # bigger is better (negative distance)
            opp_sep,
            -adj_obs_pen(nx, ny),
            -md(nx, ny, sx, sy),  # slight preference not to wander
            -dx, -dy,           # deterministic tie-break
        )
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
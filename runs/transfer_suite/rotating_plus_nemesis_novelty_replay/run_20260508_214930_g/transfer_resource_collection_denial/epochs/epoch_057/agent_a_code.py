def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Select resource where we are closer (or tie) than opponent; break ties deterministically.
    best = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Larger "score" margin is better: (opponent distance - our distance)
        margin = opd - myd
        # Prefer smaller myd among equal margin; then lexicographic on coords for determinism
        key = (-margin, myd, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty), myd, opd)
    (tx, ty) = best[1]

    dx = tx - sx
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    dy = ty - sy
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

    # Candidate moves (8 neighbors + stay), prefer those moving toward target; avoid obstacles/out of bounds.
    moves = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                continue
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                # Prefer alignment with desired direction and closeness to target
                align = (mx == step_x) + (my == step_y) + (mx == step_x and my == step_y)
                dist = cheb(nx, ny, tx, ty)
                # Deterministic ordering
                key = (-align, dist, nx, ny)
                moves.append((key, [mx, my]))
    # Add stay if needed
    stay_ok = (sx, sy) not in obs
    if stay_ok:
        moves.append(((10**9, cheb(sx, sy, tx, ty), sx, sy), [0, 0]))

    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: t[0])
    return moves[0][1]
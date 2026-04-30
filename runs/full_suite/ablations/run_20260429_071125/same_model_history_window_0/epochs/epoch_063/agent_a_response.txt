def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # Chebyshev distance for grid with diagonals
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best = None
    best_key = None
    for rx, ry in resources:
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        key = (opd - myd, -myd)  # prefer resources I'm closer to; then nearest
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    def safe_pos(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    # If opponent is already much closer to the chosen target, try to intercept by aiming for a nearby resource
    myd0 = dist((sx, sy), (tx, ty))
    opd0 = dist((ox, oy), (tx, ty))
    if opd0 + 1 < myd0 and len(resources) > 1:
        best2 = None
        best2_key = None
        for rx, ry in resources:
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            key = (-(myd), myd - opd)  # prioritize reducing my distance while not letting opponent get too far ahead
            if best2_key is None or key > best2_key:
                best2_key = key
                best2 = (rx, ry)
        tx, ty = best2

    best_move = None
    best_score = None
    for dx, dy, nx, ny in moves:
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        # Prefer lower distance to target; if ties, prefer increasing distance from opponent and moving to reduce their options
        score = (-myd, myd0 - myd, opd0 - opd)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]
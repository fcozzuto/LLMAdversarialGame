def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    center_x = (w - 1) / 2.0
    center_y = (h - 1) / 2.0

    # Pick a target we can realistically beat (or closest if none).
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        beat = opd - myd  # positive if we are closer
        center_bias = -(abs(rx - center_x) + abs(ry - center_y))
        # Prefer beat first; then shorter myd; then farther resource id to break ties deterministically.
        key = (beat, -myd, center_bias, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = None
    myd_now = cd(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        myd = cd(nx, ny, tx, ty)
        # Progress toward target and attempt to keep being ahead.
        opd = cd(ox, oy, tx, ty)
        lead = opd - myd
        progress = myd_now - myd  # positive is good
        # Small penalty if we move away from target.
        score = (lead, progress, -(abs(nx - tx) + abs(ny - ty)), -(abs(nx - ox) + abs(ny - oy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # choose best target resource by who is closer (self advantage), tie-break by closeness to self
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist2(sx, sy, rx, ry)
            do = dist2(ox, oy, rx, ry)
            score = (do - ds) * 1000000 - ds  # maximize advantage, then minimize our distance
            if best is None or score > best[0]:
                best = (score, rx, ry)
        _, tx, ty = best
        candidates = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) == (ox, oy):
                continue
            candidates.append((dist2(nx, ny, tx, ty), dx, dy))
        if candidates:
            candidates.sort()
            return [candidates[0][1], candidates[0][2]]

    # fallback: go toward center-ish or avoid obstacles, deterministic
    target_x, target_y = w // 2, h // 2
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        candidates.append((dist2(nx, ny, target_x, target_y), dx, dy))
    candidates.sort()
    return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]
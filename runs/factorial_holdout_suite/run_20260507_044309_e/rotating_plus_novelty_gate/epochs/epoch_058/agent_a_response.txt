def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        best_key = None
        for dx, dy, nx, ny in valid:
            k = (cd(nx, ny, tx, ty), dx, dy)
            if best_key is None or k < best_key:
                best_key = k
                best = (dx, dy)
        return [best[0], best[1]]

    res_set = set((rx, ry) for rx, ry in resources)

    def dmin_from(x, y):
        m = None
        for rx, ry in resources:
            d = cd(x, y, rx, ry)
            if m is None or d < m:
                m = d
        return m

    d_opp = dmin_from(ox, oy)
    best_move = (0, 0)
    best_key = None
    for dx, dy, nx, ny in valid:
        d_self = 0 if (nx, ny) in res_set else dmin_from(nx, ny)
        score = (d_opp - d_self) * 20 - d_self
        if (nx, ny) in res_set:
            score += 1000
        key = (-score, d_self, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]
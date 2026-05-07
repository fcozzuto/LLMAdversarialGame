def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def cell_score(x, y):
        best = None
        for pr in resources:
            tx, ty = int(pr[0]), int(pr[1])
            if not valid(tx, ty):
                continue
            sd = cheb(x, y, tx, ty)
            od = cheb(ox, oy, tx, ty)
            gain = od - sd
            key = (gain, -sd, tx, ty)
            if best is None or key > best[0]:
                best = (key, sd)
        if best is None:
            return (-10**9, 0)
        return (best[0][0], best[1])

    best_move = [0, 0]
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            gain, sd = cell_score(nx, ny)
            # Prefer higher gain; if similar, prefer shorter self distance; then deterministic tie-break.
            key = (gain, -sd, nx, ny)
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
    return best_move
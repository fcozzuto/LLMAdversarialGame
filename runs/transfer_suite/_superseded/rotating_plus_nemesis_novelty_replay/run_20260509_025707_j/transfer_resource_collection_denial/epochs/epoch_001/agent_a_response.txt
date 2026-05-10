def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    opts = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def cheb(a, b, c, d):
        ax = a - c
        ay = b - d
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        # Prefer being at least as close; then larger advantage; then closer; then deterministic position
        key = (0 if ds <= do else 1, -adv, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    cur_dist = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_md = None
    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        md = cheb(nx, ny, tx, ty)
        # Prefer reducing distance; break ties deterministically by move order
        key = (0 if md < cur_dist else (1 if md == cur_dist else 2), md, dx, dy)
        if best_md is None or key < best_md:
            best_md = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
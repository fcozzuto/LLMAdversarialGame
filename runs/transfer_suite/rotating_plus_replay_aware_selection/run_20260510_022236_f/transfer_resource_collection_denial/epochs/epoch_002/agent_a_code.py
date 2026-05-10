def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((x, y) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer (negative diff), then closer distance, then deterministic tie-break.
        key = (myd - opd, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    oppd_to_target = cheb(ox, oy, tx, ty)
    bestm = None
    bestmk = None
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        # Prefer moving to reduce our distance; if it makes us at least as close as opponent, prefer that too.
        mk = (myd2 - oppd_to_target > 0, myd2, abs(nx - tx) + abs(ny - ty), dx, dy)
        if bestmk is None or mk < bestmk:
            bestmk = mk
            bestm = [dx, dy]

    return bestm if bestm is not None else [0, 0]
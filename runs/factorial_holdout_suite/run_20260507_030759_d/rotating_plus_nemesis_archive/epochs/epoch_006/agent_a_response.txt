def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prioritize resources where we arrive earlier or at least not later; then nearest for us.
        key = (myd - opd, myd, tx + ty * 0.001, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Small penalty if we move into a cell adjacent to opponent (reduce interference, keep deterministic).
        adj_op = max(abs(nx - ox), abs(ny - oy)) <= 1
        key = (d, 1 if adj_op else 0, abs(dx) + abs(dy), dx, dy)
        if bestm is None or key < bestm[0]:
            bestm = (key, (dx, dy))

    if bestm is None:
        return [0, 0]
    return [bestm[1][0], bestm[1][1]]
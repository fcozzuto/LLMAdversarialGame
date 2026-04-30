def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (0, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -cheb(nx, ny, (w - 1) / 2, (h - 1) / 2)  # deterministic drift to center
            if v > best[0]:
                best = (v, (dx, dy))
        return best[1]

    best_target = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - myd, -myd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        base = -myd
        # stay away from immediate opponent targeting the same resource
        if cheb(nx, ny, tx, ty) == cheb(ox, oy, tx, ty):
            base -= 0.25
        # slight preference for reducing distance to opponent to contest indirectly
        cont = -0.05 * cheb(nx, ny, ox, oy)
        score = base + cont
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
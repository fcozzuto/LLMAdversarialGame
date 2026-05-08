def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((o[0], o[1]) for o in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        best = None
        tx = ty = None
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            delta = d_self - d_opp
            key = (delta, d_self, rx, ry)
            if best is None or key < best:
                best = key
                tx, ty = rx, ry
    else:
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        blocked = (nx, ny) in obs
        d = cheb(nx, ny, tx, ty)
        # Prefer unblocked moves; then minimize distance; then lexicographic move for determinism.
        score = (1 if blocked else 0, d, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move
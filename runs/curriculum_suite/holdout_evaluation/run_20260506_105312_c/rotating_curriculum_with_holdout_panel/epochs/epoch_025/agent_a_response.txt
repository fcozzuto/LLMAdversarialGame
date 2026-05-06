def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Deterministically pick a target to either secure (if we can arrive first) or contest (if opponent is closer).
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        secure = 0 if myd < opd else 1
        # Key: prefer securing, then nearer; within same, prefer larger "contest advantage" (opd-myd).
        key = (secure, myd, -(opd - myd), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            d_t = cheb(nx, ny, tx, ty)
            d_o = cheb(nx, ny, ox, oy)
            # Slightly discourage moves that allow opponent to "shadow" too closely.
            shadow_pen = 0 if d_o >= 3 else (3 - d_o)
            score = d_t * 10 + shadow_pen
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]
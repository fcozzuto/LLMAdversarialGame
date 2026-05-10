def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set(tuple(p) for p in obstacles)
    resources = observation.get("resources") or []

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    tx = ty = None
    if resources:
        best = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            cand = (d, d2, rx, ry)
            if best is None or cand < best:
                best = cand
                tx, ty = rx, ry

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        if tx is None:
            score = cheb(nx, ny, ox, oy)  # drift away deterministically
        else:
            score = -cheb(nx, ny, tx, ty) + 0.1 * cheb(ox, oy, tx, ty)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
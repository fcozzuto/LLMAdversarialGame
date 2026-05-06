def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid_resources = [tuple(r) for r in resources if tuple(r) not in obs]
    if not valid_resources:
        tx, ty = w // 2, h // 2
    else:
        # Pick a resource that is relatively harder for opponent than for us
        best = None
        best_key = None  # (opp_dist - self_dist, -self_dist, x+y)
        for rx, ry in valid_resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (od - sd, -sd, -(rx + ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist_to = cheb(nx, ny, tx, ty)
        dist_opp = cheb(nx, ny, ox, oy)
        opp_dist_to = cheb(ox, oy, tx, ty)  # static this turn
        # Maximize our progress while discouraging letting opponent "collapse" to the same target quickly
        score = (-(dist_to), (opp_dist_to - cheb(nx, ny, tx, ty)), -dist_opp, -(nx + ny), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
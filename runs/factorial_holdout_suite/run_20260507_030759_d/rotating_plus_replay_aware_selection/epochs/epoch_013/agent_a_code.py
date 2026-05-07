def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        obstacles.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return x < 0 or x >= w or y < 0 or y >= h or (x, y) in obstacles

    # pick best resource deterministically
    best = None
    best_d = None
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        key = (d, rx, ry)
        if best is None or key < best:
            best = key
            tx, ty = rx, ry

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_step = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        cand = (d, dx, dy)
        if best_step is None or cand < best_step:
            best_step = cand
    if best_step is None:
        return [0, 0]
    return [best_step[1], best_step[2]]
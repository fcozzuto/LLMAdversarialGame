def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    obs_set = set((p[0], p[1]) for p in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (-(od - md), md, rx, ry)  # maximize (od-md), then minimize md
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        dist = cheb(nx, ny, tx, ty)
        # prefer moves that also reduce opponent distance to the target
        oppdist = cheb(ox, oy, tx, ty)
        opp_next_hint = cheb(ox + dx, oy + dy, tx, ty)
        mkey = (dist, abs((tx - nx)) + abs((ty - ny)), opp_next_hint - oppdist, nx, ny)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
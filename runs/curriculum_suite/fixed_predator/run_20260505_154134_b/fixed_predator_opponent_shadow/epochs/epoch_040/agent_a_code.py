def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        return [0, 0]

    def opp_best_dist(tx, ty, px, py):
        best = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best:
                best = d
        return cheb(px, py, tx, ty) if best is None else best

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        move_key = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = opp_best_dist(rx, ry, ox, oy)
            key = (od - sd, -sd, -rx, -ry)
            if move_key is None or key > move_key:
                move_key = key
        if move_key is not None and (best_key is None or move_key > best_key):
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
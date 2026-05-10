def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick resource that maximizes (opponent_distance - my_distance), i.e., likely to reach first.
    best = None
    for rx, ry in resources:
        d0 = cheb(sx, sy, rx, ry)
        d1 = cheb(ox, oy, rx, ry)
        t = (d1 - d0, -(rx + ry), -d0)
        if best is None or t > best[0]:
            best = (t, rx, ry)
    _, tx, ty = best

    # Candidate moves: 8-neighborhood including stay.
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        # Prefer moves that reduce distance to target; add small tie-break to break deterministically.
        val = (-cheb(nx, ny, tx, ty), -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_val is not None else [0, 0]
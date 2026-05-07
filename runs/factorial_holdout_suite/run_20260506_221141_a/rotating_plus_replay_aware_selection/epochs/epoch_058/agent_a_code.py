def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_after_cell(nx, ny):
        if not resources:
            tx = gw - 2 if sx < gw // 2 else 1
            ty = gh - 2 if sy < gh // 2 else 1
            return -cheb(nx, ny, tx, ty)
        bestv = -10**18
        for rx, ry in resources:
            dS = cheb(nx, ny, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            # Prefer cells that keep us no slower than opponent; also prefer faster collection
            # and slight bias toward advancing toward closer resources.
            v = (dO - dS) * 100 - dS
            if dS == 0:
                v += 10**6
            bestv = v if v > bestv else bestv
        return bestv

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = best_after_cell(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move
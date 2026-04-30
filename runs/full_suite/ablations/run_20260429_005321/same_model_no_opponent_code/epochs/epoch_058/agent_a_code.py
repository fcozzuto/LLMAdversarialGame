def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    resources = [(p[0], p[1]) for p in (observation.get("resources") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))

    if not cand:
        return [0, 0]

    if resources:
        best_r = None
        best_rv = -10**18
        for rx, ry in resources:
            ds = kdist(sx, sy, rx, ry)
            do = kdist(ox, oy, rx, ry)
            rv = (do - ds) * 10 - ds
            if rv > best_rv:
                best_rv = rv
                best_r = (rx, ry)
        tx, ty = best_r
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy, nx, ny in cand:
            self_d = kdist(nx, ny, tx, ty)
            opp_d = kdist(ox, oy, tx, ty)
            # Prefer making ourselves closer and preserving/expanding distance advantage
            val = (opp_d - self_d) * 6 - self_d
            # Tie-break: prefer staying away from obstacles by choosing moves with more free neighbors
            free = 0
            for ddx, ddy in moves:
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) not in obstacles:
                    free += 1
            val += free * 0.01
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward center deterministically
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in cand:
        v = -kdist(nx, ny, cx, cy)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
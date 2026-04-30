def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = moves

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    def best_target(fromx, fromy, oppx, oppy):
        if not resources:
            return None
        best = None
        best_val = -10**18
        for rx, ry in resources:
            sd = cheb(fromx, fromy, rx, ry)
            od = cheb(oppx, oppy, rx, ry)
            # Prefer resources we can reach no later than the opponent; otherwise still allow "steal" chances.
            val = (od - sd) * 20 - obst_adj_pen(rx, ry) * 2 - sd
            if val > best_val:
                best_val = val
                best = (rx, ry)
        return best

    target = best_target(sx, sy, ox, oy)
    if target is None:
        # Drift toward opponent's corner deterministically
        tx, ty = w - 1, h - 1
    else:
        tx, ty = target

    best_move = (0, 0)
    best_h = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Greedy: reduce chebyshev distance to target; avoid stepping into obstacle-adjacent cells when tied.
        h = cheb(nx, ny, tx, ty) * 100 + obst_adj_pen(nx, ny)
        if h < best_h:
            best_h = h
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
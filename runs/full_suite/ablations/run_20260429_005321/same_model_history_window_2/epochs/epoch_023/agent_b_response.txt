def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in obst:
                pen += 1
        return pen

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    best = None
    best_sc = -10**18
    cur_opd = cheb(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        opd = cheb(nx, ny, ox, oy)
        opp_bonus = 0
        if resources:
            # Encourage moving toward resources we are closer to than the opponent.
            closer = 0
            best_my = 10**9
            best_th = 10**9
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                if d1 < best_my:
                    best_my = d1
                d2 = cheb(ox, oy, rx, ry)
                if d1 <= d2:
                    closer += 1
                if d2 < best_th:
                    best_th = d2
            # Score: prioritize reducing distance to nearest resource; prefer being closer than opponent.
            sc = (-2.5 * best_my) + (0.8 * closer) + (0.15 * (cur_opd - opd)) - (0.6 * obst_adj_pen(nx, ny))
        else:
            # No resources: just keep distance from opponent while avoiding obstacles.
            sc = (0.2 * (cur_opd - opd)) - (0.6 * obst_adj_pen(nx, ny))
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        # Only possible if all moves invalid; must return a valid delta (stay).
        return [0, 0]
    return [best[0], best[1]]
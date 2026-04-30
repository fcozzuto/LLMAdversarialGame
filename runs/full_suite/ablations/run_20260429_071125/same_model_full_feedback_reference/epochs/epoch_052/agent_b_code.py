def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in dirs:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        pos_val = 0
        if resources:
            for rx, ry in resources:
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                adv = opp_d - our_d
                if adv > 0:
                    pos_val += 50 * adv - our_d
                else:
                    pos_val -= 2 * our_d
            # Interception bias: prefer moves that reduce opponent's distance to the closest resource to them
            target = None
            best_opp_d = 10**9
            for rx, ry in resources:
                d = cheb(ox, oy, rx, ry)
                if d < best_opp_d:
                    best_opp_d = d
                    target = (rx, ry)
            if target is not None:
                tx, ty = target
                pos_val += max(0, 10 * (cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty)))
        else:
            # No visible resources: drift toward center while staying safe
            cx, cy = w // 2, h // 2
            pos_val = -cheb(nx, ny, cx, cy)

        if pos_val > best_val:
            best_val = pos_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
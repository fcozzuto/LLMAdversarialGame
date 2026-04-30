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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Choose the most favorable resource after this move.
            move_val = -10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Primary: maximize how much closer we are than opponent.
                adv = opd - myd
                # Secondary: faster pickup estimate; slight tie-break for earlier access.
                val = 1000 * adv - 2 * myd
                if val > move_val:
                    move_val = val
            # If multiple moves tie, prefer ones that don't let opponent get too much closer to any resource.
            if move_val > best_val or (move_val == best_val and cheb(nx, ny, w // 2, h // 2) < cheb(best[0] + sx, best[1] + sy, w // 2, h // 2)):
                best_val = move_val
                best = (dx, dy)
    else:
        # No resources: head toward center while keeping away from opponent.
        cx, cy = w // 2, h // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = -2 * cheb(nx, ny, cx, cy) + cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]
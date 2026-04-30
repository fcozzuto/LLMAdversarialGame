def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if resources:
            # Lead on resources: maximize (opponent distance advantage) and closeness to winning target.
            best_adv = -10**18
            best_close = 10**18
            for rx, ry in resources:
                d_my = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                adv = d_op - d_my
                if adv > best_adv or (adv == best_adv and d_my < best_close):
                    best_adv = adv
                    best_close = d_my
            # Encourage positive advantage strongly; break ties by being closer and by not drifting away from center.
            center = cheb(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0)
            v = 1000 * best_adv - best_close - 0.01 * center
        else:
            # No visible resources: move toward opponent to contest space while staying bounded.
            d_op = cheb(nx, ny, ox, oy)
            center = cheb(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0)
            v = -d_op - 0.01 * center
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def opp_step(tx, ty, px, py):
        best = (10**9, 10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, tx, ty)
            key = (d, dx, dy)
            if key < (best[0], best[2], best[3]):
                best = (d, 0, dx, dy)
        return px + best[2], py + best[3]

    center = (w // 2, h // 2)
    targets = resources[:] if resources else [center]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nsx, nsy = sx + dx, sy + dy
        if not valid(nsx, nsy):
            continue
        score = 0
        for tx, ty in targets:
            d_self = dist(nsx, nsy, tx, ty)
            nax, nay = opp_step(tx, ty, ox, oy)
            d_opp = dist(nax, nay, tx, ty)
            # Favor taking/contesting resources: make opponent farther relative to us.
            score += (d_opp - d_self)
            # Mild bias toward closer resources for us.
            score -= 0.05 * d_self
        if score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
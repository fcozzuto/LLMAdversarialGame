def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target = None
    if resources:
        bestd = 10**9
        for x, y in resources:
            d = dist_cheb(sx, sy, x, y)
            if d < bestd:
                bestd = d
                target = (x, y)
    else:
        target = ((w - 1) // 2, (h - 1) // 2)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_self = dist_cheb(nx, ny, target[0], target[1])
        d_opp = dist_cheb(nx, ny, ox, oy)
        score = -d_self + 0.02 * d_opp
        if resources:
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    score += 1000
                    break
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    if dx < -1:
        dx = -1
    if dx > 1:
        dx = 1
    if dy < -1:
        dy = -1
    if dy > 1:
        dy = 1
    return [dx, dy]
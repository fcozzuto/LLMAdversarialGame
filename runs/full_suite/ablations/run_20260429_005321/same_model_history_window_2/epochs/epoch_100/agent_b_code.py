def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    oppd = cheb(sx, sy, ox, oy)
    safe = oppd <= 2

    best_move = (0, 0)
    best_score = -10**18
    if resources and observation.get("remaining_resource_count", None) is not None:
        pass

    target_x, target_y = None, None
    if resources:
        bestr = None
        for rx, ry in resources:
            d = cheb(rx, ry, sx, sy)
            if bestr is None or d < bestr[0]:
                bestr = (d, rx, ry)
        target_x, target_y = bestr[1], bestr[2]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = 0
        if safe:
            score += 200 * cheb(nx, ny, ox, oy)
            if target_x is not None:
                score -= cheb(nx, ny, target_x, target_y)
        else:
            score += 200 * (-cheb(nx, ny, target_x, target_y)) if target_x is not None else 0
            score += cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
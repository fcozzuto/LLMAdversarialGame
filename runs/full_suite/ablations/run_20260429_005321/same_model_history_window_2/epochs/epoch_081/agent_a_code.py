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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target_score(x, y):
        if not resources:
            t = (w // 2, h // 2)
            dme = cheb(x, y, t[0], t[1])
            dop = cheb(ox, oy, t[0], t[1])
            return (dme - dop, dme, cheb(x, y, ox, oy))
        best = None
        for rx, ry in resources:
            dme = cheb(x, y, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            key = (dme - dop, dme, cheb(x, y, ox, oy), rx, ry)
            if best is None or key < best:
                best = key
        return best

    best_move = (0, 0)
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = best_target_score(nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
    if not best_key:
        return [0, 0]
    return [best_move[0], best_move[1]]
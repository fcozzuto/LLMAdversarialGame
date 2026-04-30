def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if resources:
        tx, ty = min(resources, key=lambda p: (cheb(p[0], p[1], ox, oy), cheb(p[0], p[1], sx, sy)))[0:2]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = [0, 0]
    best_score = None
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        to_target = cheb(nx, ny, tx, ty)
        to_op = cheb(nx, ny, ox, oy)
        has_resource = 1 if (nx, ny) in set(resources) else 0
        score = (-has_resource * 100000) + (-to_op) + to_target
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if not inb(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return best_move
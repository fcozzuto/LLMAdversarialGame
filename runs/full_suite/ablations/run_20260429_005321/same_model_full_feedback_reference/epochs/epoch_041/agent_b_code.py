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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target: resource where we are closest relative to opponent
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = resources[0]
        best_score = -10**18
        for x, y in resources:
            md = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            # Strongly favor states where we can beat opponent to it
            score = (od - md) * 100 - md - abs(x - (w // 2)) * 0.01 - abs(y - (h // 2)) * 0.01
            # Break ties deterministically
            score += -0.001 * (x * 17 + y * 31)
            if score > best_score:
                best_score = score
                best = (x, y)
        tx, ty = best

    # Choose move that improves our distance; if equal, reduces opponent distance.
    curd = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # prefer getting closer; then prevent opponent by making our advantage larger
        v = (curd - nd) * 100 - nd
        v += (od - nd) * 5
        if dx == 0 and dy == 0:
            v -= 0.2
        v += -0.001 * (abs(dx) + abs(dy))
        if v > best_v:
            best_v = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
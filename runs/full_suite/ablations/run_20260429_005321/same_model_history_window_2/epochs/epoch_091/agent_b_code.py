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

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    tx = ty = None
    if resources:
        best = None
        best_score = -10**18
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can arrive not later; else take best contestable one.
            score = (od - sd) * 1000 - sd
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best

    if tx is None:
        return [0, 0]

    best_move = (0, 0)
    best_move_score = -10**18
    best_dist = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_dist:
            best_dist = d
            best_move = (dx, dy)
            best_move_score = -10**18
        if d == best_dist:
            # Tie-break: maximize our advantage after the move.
            my_adv = cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)
            # smaller my_adv is better; encode
            score = -my_adv * 1000 - d
            if score > best_move_score:
                best_move_score = score
                best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
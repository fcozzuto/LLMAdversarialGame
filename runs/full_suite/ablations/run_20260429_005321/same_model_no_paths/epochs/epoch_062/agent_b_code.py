def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = ds - 0.35 * do  # prefer fast-to-reach and far from opponent
        if best_val is None or val < best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def near_obst(x, y):
        pen = 0
        for ddx in (-1, 0, 1):
            nx = x + ddx
            if nx < 0 or nx >= w:
                continue
            for ddy in (-1, 0, 1):
                ny = y + ddy
                if nx == x and ny == y:
                    continue
                if 0 <= ny < h and (nx, ny) in obstacles:
                    pen += 1
        return pen

    best_move = [0, 0]
    best_move_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ds = cheb(nx, ny, tx, ty)
        center = cheb(nx, ny, (w - 1) / 2, (h - 1) / 2)
        score = ds + 0.25 * center + 0.6 * near_obst(nx, ny)
        if best_move_score is None or score < best_move_score:
            best_move_score = score
            best_move = [dx, dy]

    return best_move
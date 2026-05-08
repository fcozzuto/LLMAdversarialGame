def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        tx, ty = resources[0]
        bestd = dist(sx, sy, tx, ty)
        for r in resources[1:]:
            d = dist(sx, sy, r[0], r[1])
            if d < bestd:
                bestd = d
                tx, ty = r[0], r[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_score = 10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = dist(nx, ny, tx, ty) + 0.15 * dist(nx, ny, ox, oy)
        if score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]
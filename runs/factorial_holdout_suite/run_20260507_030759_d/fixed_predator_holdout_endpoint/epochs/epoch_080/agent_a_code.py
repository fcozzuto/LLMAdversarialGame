def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd
        key = (adv, -sd, -((tx + ty) & 1))
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    step_options = []
    for dx, dy in ((0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            step_options.append((dx, dy))

    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        return (od2 - sd2, -sd2, -((nx + ny) & 1), -abs(dx) - abs(dy))

    best_move = None
    for dx, dy in step_options:
        sc = move_score(dx, dy)
        if best_move is None or sc > best_move[0]:
            best_move = (sc, (dx, dy))
    return [int(best_move[1][0]), int(best_move[1][1])]